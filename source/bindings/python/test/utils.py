# Copyright (c) Microsoft. All rights reserved.
# See https://aka.ms/csspeech/license201809 for the full license information.

import pytest
import requests
import sys
import time
import traceback
import azure.cognitiveservices.speech as msspeech

# the timeout to wait for session stopped event after recognition is finished
_TIMEOUT_IN_SECONDS = 30.
_SIMILARITY_SCORE_THRESHOLD = 0.80

class _TestCallback(object):
    """helper class that keeps track of how often the callback has been called, and performs checks
    on the callback arguments"""

    def __init__(self, msg, event_checks=None, fn=None, quiet=False):
        self._msg = msg
        self.num_calls = 0
        self._events = []
        self._event_checks = event_checks or (lambda x: None)
        self._fn = fn
        self._quiet = quiet

    def __call__(self, evt):
        self.num_calls += 1
        if self._msg:
            try:
                print(self._msg.format(evt=evt))
            except Exception:
                try:
                    exc_info = sys.exc_info()
                    excstring = traceback.format_exception(*exc_info)
                    print('Generic Error with {}: {}'.format(evt, excstring))
                except Exception:
                    print('error formatting exception')

        if self._fn:
            self._fn()

        exc_info = None
        try:
            self.check_event(evt)
        except AssertionError:
            try:
                exc_info = sys.exc_info()
                excstring = traceback.format_exception(*exc_info)
                if not self._quiet:
                    print('Assertion Error with {}: {}'.format(evt, excstring))
            except Exception:
                print('error formatting exception')
        except Exception:
            try:
                exc_info = sys.exc_info()
                excstring = traceback.format_exception(*exc_info)
                print('Generic Error with {}: {}'.format(evt, excstring))
            except Exception:
                print('error formatting exception')

        self._events.append((evt, exc_info))

    def check_event(self, evt):
        self._event_checks(evt)

    @property
    def events(self):
        return self._events

    def reset(self):
        self.num_calls = 0
        self._events = []


def _setup_callbacks(reco, setup_stop_callbacks=False):
    callbacks = {
            'canceled': _TestCallback('CANCELED: {evt}'),
            'recognized': _TestCallback('RECOGNIZED: {evt}'),
    }

    if not isinstance(reco, msspeech.KeywordRecognizer):
        callbacks['session_started'] = _TestCallback('SESSION_STARTED: {evt}')
        callbacks['session_stopped'] = _TestCallback('SESSION_STOPPED: {evt}')
        callbacks['recognizing'] = _TestCallback('RECOGNIZING: {evt}')

    for cb_name, callback in callbacks.items():
        callback.reset()
        getattr(reco, cb_name).connect(callback)

    def canceled_cb(evt):
        try:
            result = evt.result
            if result.reason == msspeech.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print('Speech Recognition canceled: {}'.format(cancellation_details.reason))
                print('Error details: {}'.format(cancellation_details.error_details))
                if cancellation_details.reason == msspeech.CancellationReason.Error:
                    print('Error details: {}'.format(cancellation_details.error_details))
        except Exception as e:
            print(e)

    reco.canceled.connect(canceled_cb)

    def stop(evt):
        print('STOPPING: {}'.format(evt))
        reco.stop_continuous_recognition()

    if setup_stop_callbacks:
        reco.session_stopped.connect(stop)
        reco.canceled.connect(stop)

    return callbacks


def _wait_for_event(callbacks, signal_name):
    start = time.time()
    while callbacks[signal_name].num_calls == 0:
        if time.time() - start > _TIMEOUT_IN_SECONDS:
            pytest.fail("Waiting for '{}' event timed out, giving up.".format(signal_name))
            break
        time.sleep(1.)


def _check_result_properties(result):
    """check that properties are defined on recognition result. In particular, check that
    recognition latency is exposed on final results."""
    assert type(result.properties) is dict
    if result.reason in (msspeech.ResultReason.RecognizedSpeech,
            msspeech.ResultReason.TranslatedSpeech, msspeech.ResultReason.RecognizedIntent):
        latency = result.properties[msspeech.PropertyId.SpeechServiceResponse_RecognitionLatencyMs]
        assert int(latency) > 0, (result, result.reason)
    else:
        pass

    error_json_property_id = msspeech.PropertyId.SpeechServiceResponse_JsonErrorDetails
    if result.reason is msspeech.ResultReason.Canceled and result.cancellation_details.reason != \
            msspeech.CancellationReason.EndOfStream:
        assert error_json_property_id in result.properties, (result.reason, result,
                str(result.cancellation_details))
        error_json = result.properties[error_json_property_id]
        assert error_json, result.reason
    else:
        assert error_json_property_id not in result.properties, result.reason


def _check_callbacks(callbacks, check_num_recognized=True):
    assert callbacks['session_started'].num_calls == 1
    assert callbacks['session_stopped'].num_calls == 1
    # It is possible that service sends final result directly without intermediate results, thus not expecting intermediate always comes
    #assert callbacks['recognizing'].num_calls >= 1
    if check_num_recognized:
        assert callbacks['recognized'].num_calls == 1


def _check_result_common(result, speech_input, utterance_index, do_check_duration=True,
        do_check_offset=True):
    similarity_ratio = _levenshtein_ratio(speech_input.transcription[utterance_index].lower(), result.text.lower())
    assert similarity_ratio > _SIMILARITY_SCORE_THRESHOLD
    if do_check_duration:
        assert result.duration > 0
    if do_check_offset:
        assert result.offset > 0
    assert isinstance(result.result_id, str)
    assert result.result_id
    assert result.cancellation_details is None
    assert result.no_match_details is None
    assert result.json
    assert '' == result.error_json

    _check_result_properties(result)


def _check_sr_result(result, speech_input, utterance_index):
    assert isinstance(result, msspeech.SpeechRecognitionResult)
    assert msspeech.ResultReason.RecognizedSpeech == result.reason

    _check_result_common(result, speech_input, utterance_index)


def _check_translation_result(result, speech_input, utterance_index, target_languages):
    assert isinstance(result, msspeech.translation.TranslationRecognitionResult)
    assert msspeech.ResultReason.TranslatedSpeech == result.reason

    assert set(result.translations.keys()) == set(target_languages)
    for language in target_languages:
        similarity_ratio = _levenshtein_ratio(speech_input.translations[language].lower(), result.translations[language].lower())
        assert similarity_ratio > _SIMILARITY_SCORE_THRESHOLD

    _check_result_common(result, speech_input, utterance_index)


def _check_intent_result(result, intent_input, utterance_index):
    assert isinstance(result, msspeech.intent.IntentRecognitionResult)
    assert intent_input.intent_id == result.intent_id
    assert isinstance(result.intent_json, str)
    assert result.intent_json

    _check_result_common(result, intent_input, utterance_index, do_check_duration=False,
            do_check_offset=False)


def get_token(subscription, region):
    """retireve an authorization token for the Speech Service"""
    fetch_token_url = "https://{}.api.cognitive.microsoft.com/sts/v1.0/issueToken".format(region)
    headers = {
        'Ocp-Apim-Subscription-Key': subscription
    }
    response = requests.post(fetch_token_url, headers=headers)
    return str(response.text)

def _levenshtein_ratio(str1, str2):
    m = len(str1)
    n = len(str2)
    lensum = float(m + n)
    d = []           
    for i in range(m+1):
        d.append([i])        
    del d[0][0]    
    for j in range(n+1):
        d[0].append(j)       
    for j in range(1,n+1):
        for i in range(1,m+1):
            if str1[i-1] == str2[j-1]:
                d[i].insert(j,d[i-1][j-1])           
            else:
                minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+2)         
                d[i].insert(j, minimum)
    ldist = d[-1][-1]
    ratio = (lensum - ldist)/lensum
    return ratio