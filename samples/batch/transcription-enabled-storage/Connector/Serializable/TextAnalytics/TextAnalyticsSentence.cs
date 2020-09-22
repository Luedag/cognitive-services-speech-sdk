// <copyright file="TextAnalyticsSentence.cs" company="Microsoft Corporation">
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
// </copyright>

namespace Connector.Serializable.TextAnalytics
{
    public class TextAnalyticsSentence
    {
        public TextAnalyticsSentence(TextAnalyticsScores sentenceScores)
        {
            SentenceScores = sentenceScores;
        }

        public TextAnalyticsScores SentenceScores { get; private set; }
    }
}
