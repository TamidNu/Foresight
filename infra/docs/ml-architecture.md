# how tf do we build and dpeloy the numerous layers of our application?

1. we need to be able to POLL REAL TIME DATA (eg: bon jovi just announced his tour in ireland, the hotel sold out within an hour. This will require more than just analysing EXISTING data, we will need to leverage 3rd party APIs )
2. Be able to detect patterns of occupancy across the data we possess
3. be able to derive arbitraty insights from the current guestline BMS data (which we should be getting access to in the next ~ 2 weeks)
4. Reccomend a pricing strategy based on this
5. I have no idea how to do DS on this scale and to deploy it, so we will need to do a little more research, also our DS/ML pricing model will have Multiple layers, and one of the layers can be an OpenAI API call to get a short reasoning for why we are predicting what we are pridicting
