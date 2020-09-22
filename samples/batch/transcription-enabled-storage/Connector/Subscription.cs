// <copyright file="Subscription.cs" company="Microsoft Corporation">
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
// </copyright>

namespace Connector
{
    using System;

    public class Subscription
    {
        public Subscription(string subscriptionKey, Uri locationUri)
        {
            SubscriptionKey = subscriptionKey;
            LocationUri = locationUri;
        }

        public string SubscriptionKey { get; }

        public Uri LocationUri { get; }
    }
}
