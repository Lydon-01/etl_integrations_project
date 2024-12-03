                            ++                                                   
     %%%%%%%%    %%%%%%%%    +++   ++   ++    +++    +++++     ++     +++++      
         %%%     %%         %  +++ ++    ++  ++    ++    +     ++   ++    ++     
        %%%     %%%%%%%     %%%  ++++     ++++     ++++++      ++   ++++++       
       %%        %%         %%%%%  ++      ++           +++    ++        +++     
      %%         %%         %%  %%%        ++      ++    ++    ++   ++    ++     
     %%%%%%%%    %%%%%%%%   %%    %%%      ++        ++++      ++     ++++       
                                    %%                                           


# Systems Integration Project - Implementation plan (Q4/2024)
> Owner: LydonCarter@gmail.com
> Work session 1: 27 Nov - 3 Dec 2024 | Estimate 15 hours

## Background
Deloy a standalone Python data pipeline package. Source data is retrived via API call. 
Put the datainto a PSQL database. 
Limitted time to build (3h)

# Ideas for future:

### Extract Ideas
- Pull the data of all African Contries, and create metric of a certain field. 

### Transformation Ideas
- Potentially compare the metric to developed nation, to show progress over time. 

### Load Ideas 
- Can this be run as a Streaming Job?
- Design table format

### Metrics/Monitoring 
- can I record my time spent
- track job duration 
- data processed 
- data quality
- backwards compatiblity
- *backfill or aggregation features

### UI
- expose ways to interact
  - benchmark/testing of new ETL versions
  - stop/start job
- display dashboard of data findings
- stop and 
