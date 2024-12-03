# What are we looking for in a system integration engineer?

We are looking for backend engineering candidates that have worked on integrating software systems and are proficient in data structures and algorithms.

Now, before we start. Let's apply the algorithm of success:

```js
while(noSuccess) {
    tryAgain();
    if(Dead) {
        break;
    }
}
```

# Assessment:

Build an ETL pipeline application that uses Python and a PostgreSQL database. The application should extract  data from the [GHO OData API](https://www.who.int/data/gho/info/gho-odata-api) and process that data in any way you see fit, finally ingesting that into the postgres database.

## What are we testing for in this assessment?

- Your skill as a back-end developer.
- Your ability to write readable and extendable code by following the right design principles.
- Your ability to transform data into a format that can support analysis.
- Your ability to think about a software product from end to end.

## Expectations

- Although we strive for perfection we don't expect everything to be perfect, **just do you**.
- Given the size of the assignment we don't expect everything to be done, **do what you can given the time**.
- We don't expect you to import the `WHO GHO OData API` data in any specific way, **use your own initiative**.
- We don't expect you to fetch all data sets, **choose the one you feel is the most important**.

> The assignment should take about 3 hours to complete.

## Requirements:

- Tech Stack
  - [ ] Python backend
  - [ ] Postgres database
- [ ] Data Validation
- [ ] Edge cases
- [ ] Define your approach testing and debugging 
- [ ] Setup instructions (README etc)

## Bonus Points:

- [ ] The pipeline can be stopped and resumed.
- [ ] The ability to re-run, only fetch the most recent data.
- [ ] The E of ETL can be stopped and resumed without need to restart the data pull from scratch.
- [ ] Any form of tests (unit/functional)
- [ ] Additional suggestions if you had more time

## Overview

Provide a brief written explanation (just a paragraph or so) of your work and decisions.

## Demo

Add screenshots/recording of your project.

## Hints

- Consider the intermediary data structures you would use in your application, and if possible comment on efficiency.
- A whole working product is more important than fetching all data sets.
- Clear and easy to understand setup instructions.
- Can you run this as-is on another OS?
- Keep it simple...
- Have fun!
