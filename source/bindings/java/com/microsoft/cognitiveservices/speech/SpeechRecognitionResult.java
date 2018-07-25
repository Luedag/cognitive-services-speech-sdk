package com.microsoft.cognitiveservices.speech;
//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

import com.microsoft.cognitiveservices.speech.internal.RecognitionResult;
import com.microsoft.cognitiveservices.speech.internal.ResultPropertyValueCollection;
import com.microsoft.cognitiveservices.speech.util.Contracts;

import java.math.BigInteger;

/**
  * Defines result of speech recognition.
  */
public class SpeechRecognitionResult {

    private String resultId;
    private RecognitionStatus reason;
    private String text;
    private RecognitionResultCollection properties;
    private long duration;
    private long offset;

    protected SpeechRecognitionResult(RecognitionResult result) {
        Contracts.throwIfNull(result, "result");

        resultId = result.getResultId();
        text = result.getText();
        BigInteger tenThousand = BigInteger.valueOf(10000);
        duration = result.Duration().divide(tenThousand).longValue();
        offset = result.Offset().divide(tenThousand).longValue();
        reason = RecognitionStatus.values()[result.getReason().swigValue()];
        properties = new RecognitionResultCollection(result.getProperties());

        Contracts.throwIfNull(resultId, "resultId");
    }

    /**
      * Specifies the result identifier.
      * @return Specifies the result identifier.
      */
    public String getResultId() {
        return resultId;
    }
    
    /**
      * Specifies status of the result.
      * @return Specifies status of the result.
      */
    public RecognitionStatus getReason() {
        return reason;
    }

    /**
      * Presents the recognized text in the result.
      * @return Presents the recognized text in the result.
      */
    public String getText() {
        return text;
    }

    /**
      * Duration of recognized speech in milliseconds.
      * @return Duration of recognized speech in milliseconds.
      */
    public long getDuration() {
        return duration;
    }

    /**
      * Offset of recognized speech in milliseconds.
      * @return Offset of recognized speech in milliseconds.
      */
    public long getOffset() {
        return offset;
    }

    /**
    * In case of an unsuccessful recognition, provides a brief description of an occurred error.
    * This field is only filled-out if the recognition status (@see RecognitionStatus) is set to Canceled.
    * @return a brief description of an error.
    */
    public String getErrorDetails() {
        return properties.getString(ResultParameterNames.ErrorDetails);
    }

    /**
    * A string containing Json serialized recognition result as it was received from the service.
    * @return Json serialized representation of the result.
    */
    public String getJson() {
      return properties.getString(ResultParameterNames.Json);
    }

    /**
     *  The set of properties exposed in the result.
     * @return The set of properties exposed in the result.
     */
    public RecognitionResultCollection getProperties() {
        return properties;
    }

    /**
      * Returns a String that represents the speech recognition result.
      * @return A String that represents the speech recognition result.
      */
    @Override
    public String toString() {
        return "ResultId:" + resultId +
               " Status:" + reason +
               " Recognized text:<" + text +
               ">.";
    }
    
    public class RecognitionResultCollection
    {
        ResultPropertyValueCollection _collection;
        
        RecognitionResultCollection(ResultPropertyValueCollection collection)
        {
            Contracts.throwIfNull(collection, "collection");

            _collection = collection;
        }
        
        /**
         * Checks whether the parameter specified by name has a String value.
         *
         * @param name The parameter name.
         * @return true if the parameter has a value, and false otherwise.
         */
       public boolean isString(String name) {
            Contracts.throwIfNull(name, "name");
           
           return _collection.ContainsString(name);
       }

       /**
         * Checks whether the parameter specified by name has an Int value.
         *
         * @param name The parameter name.
         * @return true if the parameter has a value, and false otherwise.
         */
       public boolean isInt(String name) {
            Contracts.throwIfNull(name, "name");
           
           return _collection.ContainsNumber(name);
       }

       /**
         * Checks whether the parameter specified by name has a Boolean value.
         *
         * @param name The parameter name.
         * @return true if the parameter has a value, and false otherwise.
         */
       public boolean isBool(String name) {
            Contracts.throwIfNull(name, "name");
           
           return _collection.ContainsBool(name);
       }

       /**
         * Returns the parameter value in type String. The parameter must have the same type as String.
         * If the name is not available, it returns an empty String.
         *
         * @param name The parameter name.
         * @return value of the parameter.
         */
       public String getString(String name) {
           return getString(name, "");
       }
       
       /**
        * Returns the parameter value in type int. The parameter must have the same type as int.
        * If the name is not available, it returns 0.
        *
        * @param name The parameter name.
        * @return value of the parameter.
        */
       public int getInt(String name) {
           return getInt(name, 0);
       }
       
       /**
        * Returns the parameter value in type boolean. The parameter must have the same type as boolean.
        * If the name is not available, it returns false.
        *
        * @param name The parameter name.
        * @return value of the parameter.
        */
       public boolean getBool(String name) {
           return getBool(name, false);
       }
       
       /**
         * Returns the parameter value in type String. The parameter must have the same type as String.
         * Currently only String, int and bool are allowed.
         * If the name is not available, the specified defaultValue is returned.
         *
         * @param name The parameter name.
         * @param defaultValue The default value which is returned if the parameter is not available in the collection.
         * @return value of the parameter.
         */
       public String getString(String name, String defaultValue) {
           Contracts.throwIfNull(name, "name");

           return _collection.GetString(name, defaultValue);
       }

       /**
         * Returns the parameter value in type int. The parameter must have the same type as int.
         * Currently only String, int and bool are allowed.
         * If the name is not available, the specified defaultValue is returned.
         *
         * @param name The parameter name.
         * @param defaultValue The default value which is returned if the parameter is not available in the collection.
         * @return value of the parameter.
         */
       public int getInt(String name, int defaultValue) {
           Contracts.throwIfNull(name, "name");

           return _collection.GetNumber(name, defaultValue);
       }

       /**
         * Returns the parameter value in type boolean. The parameter must have the same type as boolean.
         * Currently only String, int and bool are allowed.
         * If the name is not available, the specified defaultValue is returned.
         *
         * @param name The parameter name.
         * @param defaultValue The default value which is returned if the parameter is not available in the collection.
         * @return value of the parameter.
         */
       public boolean getBool(String name, boolean defaultValue) {
           Contracts.throwIfNull(name, "name");

           return _collection.GetBool(name, defaultValue);
       }
    }
}