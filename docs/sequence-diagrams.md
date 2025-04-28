# Sequence Diagrams for Key Workflows

This document provides sequence diagrams for key workflows in the pAIssive Income framework, illustrating how different components interact during various processes.

## 1. Niche Analysis Workflow

The following sequence diagram illustrates the niche analysis workflow, from user input to niche selection:

```
+-------+       +------------+       +-----------------+       +------------------+
| User  |       | Web        |       | Agent Team      |       | Niche Analysis   |
|       |       | Interface  |       |                 |       | Module           |
+-------+       +------------+       +-----------------+       +------------------+
    |                 |                     |                          |
    | 1. Select market|                     |                          |
    | segments        |                     |                          |
    |---------------->|                     |                          |
    |                 | 2. Request niche    |                          |
    |                 | analysis            |                          |
    |                 |-------------------->|                          |
    |                 |                     | 3. Initialize            |
    |                 |                     | researcher agent         |
    |                 |                     |------------------------->|
    |                 |                     |                          |
    |                 |                     |                          |
    |                 |                     | 4. Analyze market        |
    |                 |                     | segments                 |
    |                 |                     |------------------------->|
    |                 |                     |                          |
    |                 |                     |                          |
    |                 |                     |      5. Identify niches  |
    |                 |                     |<-------------------------|
    |                 |                     |                          |
    |                 |                     | 6. Calculate             |
    |                 |                     | opportunity scores       |
    |                 |                     |------------------------->|
    |                 |                     |                          |
    |                 |                     |      7. Return scored    |
    |                 |                     |      niches              |
    |                 |                     |<-------------------------|
    |                 |                     |                          |
    |                 | 8. Return niche     |                          |
    |                 | analysis results    |                          |
    |                 |<--------------------|                          |
    |                 |                     |                          |
    | 9. Display      |                     |                          |
    | niche options   |                     |                          |
    |<----------------|                     |                          |
    |                 |                     |                          |
    | 10. Select      |                     |                          |
    | niche           |                     |                          |
    |---------------->|                     |                          |
    |                 | 11. Update project  |                          |
    |                 | state               |                          |
    |                 |-------------------->|                          |
    |                 |                     |                          |
    |                 | 12. Confirm         |                          |
    |                 | selection           |                          |
    |                 |<--------------------|                          |
    |                 |                     |                          |
    | 13. Show        |                     |                          |
    | confirmation    |                     |                          |
    |<----------------|                     |                          |
    |                 |                     |                          |
```

## 2. Solution Development Workflow

The following sequence diagram illustrates the solution development workflow, from niche selection to solution design:

```
+-------+       +------------+       +-------------+       +--------------+       +--------------+
| User  |       | Web        |       | Agent Team  |       | Developer    |       | AI Models    |
|       |       | Interface  |       |             |       | Agent        |       | Module       |
+-------+       +------------+       +-------------+       +--------------+       +--------------+
    |                 |                    |                     |                      |
    | 1. Request      |                    |                     |                      |
    | solution dev    |                    |                     |                      |
    |---------------->|                    |                     |                      |
    |                 | 2. Start solution  |                     |                      |
    |                 | development        |                     |                      |
    |                 |------------------->|                     |                      |
    |                 |                    | 3. Get niche and    |                      |
    |                 |                    | problem data        |                      |
    |                 |                    |-------------------->|                      |
    |                 |                    |                     |                      |
    |                 |                    |                     | 4. Request AI        |
    |                 |                    |                     | assistance           |
    |                 |                    |                     |--------------------->|
    |                 |                    |                     |                      |
    |                 |                    |                     |      5. Generate     |
    |                 |                    |                     |      solution ideas  |
    |                 |                    |                     |<---------------------|
    |                 |                    |                     |                      |
    |                 |                    |                     | 6. Design            |
    |                 |                    |                     | technology stack     |
    |                 |                    |                     |--------------------->|
    |                 |                    |                     |                      |
    |                 |                    |                     |      7. Recommend    |
    |                 |                    |                     |      technologies    |
    |                 |                    |                     |<---------------------|
    |                 |                    |                     |                      |
    |                 |                    |                     | 8. Create solution   |
    |                 |                    |                     | design               |
    |                 |                    |                     |----------------------|
    |                 |                    |                     |                      |
    |                 |                    |     9. Return       |                      |
    |                 |                    |     solution design |                      |
    |                 |                    |<--------------------|                      |
    |                 |                    |                     |                      |
    |                 | 10. Return         |                     |                      |
    |                 | solution design    |                     |                      |
    |                 |<-------------------|                     |                      |
    |                 |                    |                     |                      |
    | 11. Display     |                    |                     |                      |
    | solution design |                    |                     |                      |
    |<----------------|                    |                     |                      |
    |                 |                    |                     |                      |
    | 12. Approve     |                    |                     |                      |
    | design          |                    |                     |                      |
    |---------------->|                    |                     |                      |
    |                 | 13. Update project |                     |                      |
    |                 | state              |                     |                      |
    |                 |------------------->|                     |                      |
    |                 |                    |                     |                      |
    |                 | 14. Confirm        |                     |                      |
    |                 | update             |                     |                      |
    |                 |<-------------------|                     |                      |
    |                 |                    |                     |                      |
    | 15. Show        |                    |                     |                      |
    | confirmation    |                    |                     |                      |
    |<----------------|                    |                     |                      |
    |                 |                    |                     |                      |
```

## 3. Monetization Strategy Workflow

The following sequence diagram illustrates the monetization strategy workflow:

```
+-------+       +------------+       +-------------+       +----------------+       +--------------+
| User  |       | Web        |       | Agent Team  |       | Monetization   |       | Monetization |
|       |       | Interface  |       |             |       | Agent          |       | Module       |
+-------+       +------------+       +-------------+       +----------------+       +--------------+
    |                 |                    |                       |                      |
    | 1. Request      |                    |                       |                      |
    | monetization    |                    |                       |                      |
    | strategy        |                    |                       |                      |
    |---------------->|                    |                       |                      |
    |                 | 2. Start           |                       |                      |
    |                 | monetization       |                       |                      |
    |                 | strategy dev       |                       |                      |
    |                 |------------------->|                       |                      |
    |                 |                    | 3. Get solution       |                      |
    |                 |                    | design data           |                      |
    |                 |                    |---------------------->|                      |
    |                 |                    |                       |                      |
    |                 |                    |                       | 4. Analyze pricing   |
    |                 |                    |                       | options              |
    |                 |                    |                       |--------------------->|
    |                 |                    |                       |                      |
    |                 |                    |                       |      5. Return       |
    |                 |                    |                       |      pricing models  |
    |                 |                    |                       |<---------------------|
    |                 |                    |                       |                      |
    |                 |                    |                       | 6. Create            |
    |                 |                    |                       | subscription plans   |
    |                 |                    |                       |--------------------->|
    |                 |                    |                       |                      |
    |                 |                    |                       |      7. Return       |
    |                 |                    |                       |      subscription    |
    |                 |                    |                       |      plans           |
    |                 |                    |                       |<---------------------|
    |                 |                    |                       |                      |
    |                 |                    |                       | 8. Calculate         |
    |                 |                    |                       | revenue              |
    |                 |                    |                       | projections          |
    |                 |                    |                       |--------------------->|
    |                 |                    |                       |                      |
    |                 |                    |                       |      9. Return       |
    |                 |                    |                       |      revenue         |
    |                 |                    |                       |      projections     |
    |                 |                    |                       |<---------------------|
    |                 |                    |                       |                      |
    |                 |                    |                       | 10. Finalize         |
    |                 |                    |                       | strategy             |
    |                 |                    |                       |----------------------|
    |                 |                    |                       |                      |
    |                 |                    |     11. Return        |                      |
    |                 |                    |     monetization      |                      |
    |                 |                    |     strategy          |                      |
    |                 |                    |<----------------------|                      |
    |                 |                    |                       |                      |
    |                 | 12. Return         |                       |                      |
    |                 | monetization       |                       |                      |
    |                 | strategy           |                       |                      |
    |                 |<-------------------|                       |                      |
    |                 |                    |                       |                      |
    | 13. Display     |                    |                       |                      |
    | strategy        |                    |                       |                      |
    |<----------------|                    |                       |                      |
    |                 |                    |                       |                      |
    | 14. Approve     |                    |                       |                      |
    | strategy        |                    |                       |                      |
    |---------------->|                    |                       |                      |
    |                 | 15. Update project |                       |                      |
    |                 | state              |                       |                      |
    |                 |------------------->|                       |                      |
    |                 |                    |                       |                      |
    |                 | 16. Confirm        |                       |                      |
    |                 | update             |                       |                      |
    |                 |<-------------------|                       |                      |
    |                 |                    |                       |                      |
    | 17. Show        |                    |                       |                      |
    | confirmation    |                    |                       |                      |
    |<----------------|                    |                       |                      |
    |                 |                    |                       |                      |
```

## 4. Marketing Campaign Workflow

The following sequence diagram illustrates the marketing campaign workflow:

```
+-------+       +------------+       +-------------+       +----------------+       +--------------+
| User  |       | Web        |       | Agent Team  |       | Marketing      |       | Marketing    |
|       |       | Interface  |       |             |       | Agent          |       | Module       |
+-------+       +------------+       +-------------+       +----------------+       +--------------+
    |                 |                    |                       |                      |
    | 1. Request      |                    |                       |                      |
    | marketing       |                    |                       |                      |
    | campaign        |                    |                       |                      |
    |---------------->|                    |                       |                      |
    |                 | 2. Start marketing |                       |                      |
    |                 | campaign dev       |                       |                      |
    |                 |------------------->|                       |                      |
    |                 |                    | 3. Get solution and   |                      |
    |                 |                    | monetization data     |                      |
    |                 |                    |---------------------->|                      |
    |                 |                    |                       |                      |
    |                 |                    |                       | 4. Create user       |
    |                 |                    |                       | personas             |
    |                 |                    |                       |--------------------->|
    |                 |                    |                       |                      |
    |                 |                    |                       |      5. Return       |
    |                 |                    |                       |      user personas   |
    |                 |                    |                       |<---------------------|
    |                 |                    |                       |                      |
    |                 |                    |                       | 6. Analyze           |
    |                 |                    |                       | marketing channels   |
    |                 |                    |                       |--------------------->|
    |                 |                    |                       |                      |
    |                 |                    |                       |      7. Return       |
    |                 |                    |                       |      channel         |
    |                 |                    |                       |      recommendations |
    |                 |                    |                       |<---------------------|
    |                 |                    |                       |                      |
    |                 |                    |                       | 8. Generate          |
    |                 |                    |                       | content templates    |
    |                 |                    |                       |--------------------->|
    |                 |                    |                       |                      |
    |                 |                    |                       |      9. Return       |
    |                 |                    |                       |      content         |
    |                 |                    |                       |      templates       |
    |                 |                    |                       |<---------------------|
    |                 |                    |                       |                      |
    |                 |                    |                       | 10. Create           |
    |                 |                    |                       | content strategy     |
    |                 |                    |                       |--------------------->|
    |                 |                    |                       |                      |
    |                 |                    |                       |      11. Return      |
    |                 |                    |                       |      content         |
    |                 |                    |                       |      strategy        |
    |                 |                    |                       |<---------------------|
    |                 |                    |                       |                      |
    |                 |                    |                       | 12. Finalize         |
    |                 |                    |                       | marketing plan       |
    |                 |                    |                       |----------------------|
    |                 |                    |                       |                      |
    |                 |                    |     13. Return        |                      |
    |                 |                    |     marketing plan    |                      |
    |                 |                    |<----------------------|                      |
    |                 |                    |                       |                      |
    |                 | 14. Return         |                       |                      |
    |                 | marketing plan     |                       |                      |
    |                 |<-------------------|                       |                      |
    |                 |                    |                       |                      |
    | 15. Display     |                    |                       |                      |
    | marketing plan  |                    |                       |                      |
    |<----------------|                    |                       |                      |
    |                 |                    |                       |                      |
    | 16. Approve     |                    |                       |                      |
    | marketing plan  |                    |                       |                      |
    |---------------->|                    |                       |                      |
    |                 | 17. Update project |                       |                      |
    |                 | state              |                       |                      |
    |                 |------------------->|                       |                      |
    |                 |                    |                       |                      |
    |                 | 18. Confirm        |                       |                      |
    |                 | update             |                       |                      |
    |                 |<-------------------|                       |                      |
    |                 |                    |                       |                      |
    | 19. Show        |                    |                       |                      |
    | confirmation    |                    |                       |                      |
    |<----------------|                    |                       |                      |
    |                 |                    |                       |                      |
```

## 5. Model Inference and Caching Workflow

The following sequence diagram illustrates the AI model inference process with caching:

```
+------------+       +-------------+       +--------------+       +----------+       +----------+
| Client     |       | Model       |       | Model        |       | Cache    |       | Model    |
| Application|       | Manager     |       | Adapter      |       | Service  |       | Provider |
+------------+       +-------------+       +--------------+       +----------+       +----------+
      |                     |                     |                    |                  |
      | 1. Request          |                     |                    |                  |
      | inference           |                     |                    |                  |
      |-------------------->|                     |                    |                  |
      |                     | 2. Check cache      |                    |                  |
      |                     |--------------------- ------------------>|                  |
      |                     |                     |                    |                  |
      |                     |                     |     3. Return      |                  |
      |                     |                     |     cache result   |                  |
      |                     |<-------------------- -------------------|                  |
      |                     |                     |                    |                  |
      |                     | 4. If cache miss,   |                    |                  |
      |                     | select adapter      |                    |                  |
      |                     |-------------------->|                    |                  |
      |                     |                     |                    |                  |
      |                     |                     | 5. Prepare         |                  |
      |                     |                     | input              |                  |
      |                     |                     |--------------------|---------------->|
      |                     |                     |                    |                  |
      |                     |                     |                    |     6. Process   |
      |                     |                     |                    |     inference    |
      |                     |                     |                    |<-----------------|
      |                     |                     |                    |                  |
      |                     |                     | 7. Get inference   |                  |
      |                     |                     | result             |                  |
      |                     |                     |<-------------------|-----------------|
      |                     |                     |                    |                  |
      |                     |                     | 8. Post-process    |                  |
      |                     |                     | result             |                  |
      |                     |                     |--------------------|-----------------|
      |                     |                     |                    |                  |
      |                     | 9. Cache result     |                    |                  |
      |                     |--------------------- ------------------>|                  |
      |                     |                     |                    |                  |
      |                     |    10. Return       |                    |                  |
      |                     |    inference result |                    |                  |
      |                     |<--------------------|                    |                  |
      |                     |                     |                    |                  |
      | 11. Return          |                     |                    |                  |
      | inference result    |                     |                    |                  |
      |<--------------------|                     |                    |                  |
      |                     |                     |                    |                  |
```

## 6. Model Deployment Workflow

The following sequence diagram illustrates the model deployment process:

```
+-------+       +-------------+       +----------------+       +----------------+       +------------+
| User  |       | AI Models   |       | Docker         |       | Cloud          |       | Cloud      |
|       |       | Module      |       | Deployment     |       | Deployment     |       | Provider   |
+-------+       +-------------+       +----------------+       +----------------+       +------------+
    |                 |                       |                       |                      |
    | 1. Request      |                       |                       |                      |
    | model deployment|                       |                       |                      |
    |---------------->|                       |                       |                      |
    |                 | 2. Create deployment  |                       |                      |
    |                 | configuration         |                       |                      |
    |                 |---------------------->|                       |                      |
    |                 |                       |                       |                      |
    |                 |                       | 3. Generate Docker    |                      |
    |                 |                       | configuration files   |                      |
    |                 |                       |---------------------->|                      |
    |                 |                       |                       |                      |
    |                 |                       |                       | 4. Generate cloud    |
    |                 |                       |                       | deployment files     |
    |                 |                       |                       |--------------------->|
    |                 |                       |                       |                      |
    |                 |                       |                       |     5. Return        |
    |                 |                       |                       |     deployment       |
    |                 |                       |                       |     confirmation     |
    |                 |                       |                       |<---------------------|
    |                 |                       |                       |                      |
    |                 |                       |     6. Return         |                      |
    |                 |                       |     configuration     |                      |
    |                 |                       |     files path        |                      |
    |                 |                       |<----------------------|                      |
    |                 |                       |                       |                      |
    |                 | 7. Return deployment  |                       |                      |
    |                 | file paths            |                       |                      |
    |                 |<----------------------|                       |                      |
    |                 |                       |                       |                      |
    | 8. Return       |                       |                       |                      |
    | deployment info |                       |                       |                      |
    |<----------------|                       |                       |                      |
    |                 |                       |                       |                      |
    | 9. Execute      |                       |                       |                      |
    | deployment      |                       |                       |                      |
    | script          |                       |                       |                      |
    |-------------------------------------- directly ---------------------------------------->|
    |                 |                       |                       |                      |
    |                 |                       |                       |                      |
    |                 |                       |                       |      10. Deploy      |
    |                 |                       |                       |      model service   |
    |                 |                       |                       |<---------------------|
    |                 |                       |                       |                      |
    |                 |                       |                       |      11. Return      |
    |                 |                       |                       |      service URL     |
    |<-----------------------------------------------------------------------------|
    |                 |                       |                       |                      |
```

## 7. Model Fallback Workflow

The following sequence diagram illustrates the model fallback process when a primary model is unavailable:

```
+-----------------+       +------------------+       +----------------+       +------------------+
| Client          |       | Model            |       | Fallback       |       | Performance      |
| Application     |       | Manager          |       | Manager        |       | Monitor          |
+-----------------+       +------------------+       +----------------+       +------------------+
        |                          |                         |                         |
        | 1. Request               |                         |                         |
        | model inference          |                         |                         |
        |------------------------->|                         |                         |
        |                          |                         |                         |
        |                          | 2. Try to load          |                         |
        |                          | primary model           |                         |
        |                          |------------------X      |                         |
        |                          | (Model not available)   |                         |
        |                          |                         |                         |
        |                          | 3. Request fallback     |                         |
        |                          | model                   |                         |
        |                          |------------------------>|                         |
        |                          |                         |                         |
        |                          |                         | 4. Determine            |
        |                          |                         | fallback strategy       |
        |                          |                         |------------------------>|
        |                          |                         |                         |
        |                          |                         |      5. Return model    |
        |                          |                         |      usage metrics      |
        |                          |                         |<------------------------|
        |                          |                         |                         |
        |                          |                         | 6. Find suitable        |
        |                          |                         | fallback model          |
        |                          |                         |-------------------------|
        |                          |                         |                         |
        |                          |      7. Return          |                         |
        |                          |      fallback model     |                         |
        |                          |<------------------------|                         |
        |                          |                         |                         |
        |                          | 8. Load fallback        |                         |
        |                          | model                   |                         |
        |                          |-------------------------|                         |
        |                          |                         |                         |
        |                          | 9. Log fallback         |                         |
        |                          | event                   |                         |
        |                          |------------------------>|                         |
        |                          |                         |                         |
        |                          |                         | 10. Record              |
        |                          |                         | fallback metrics        |
        |                          |                         |------------------------>|
        |                          |                         |                         |
        | 11. Return               |                         |                         |
        | inference result         |                         |                         |
        |<-------------------------|                         |                         |
        |                          |                         |                         |
```

## 8. User Authentication Workflow

The following sequence diagram illustrates the user authentication process:

```
+-------+       +------------+       +-------------------+       +------------------+       +------------+
| User  |       | Web        |       | Authentication    |       | User             |       | Session    |
|       |       | Interface  |       | Service           |       | Database         |       | Manager    |
+-------+       +------------+       +-------------------+       +------------------+       +------------+
    |                 |                       |                          |                      |
    | 1. Submit login |                       |                          |                      |
    | credentials     |                       |                          |                      |
    |---------------->|                       |                          |                      |
    |                 | 2. Forward            |                          |                      |
    |                 | credentials           |                          |                      |
    |                 |---------------------->|                          |                      |
    |                 |                       |                          |                      |
    |                 |                       | 3. Validate              |                      |
    |                 |                       | credentials              |                      |
    |                 |                       |------------------------->|                      |
    |                 |                       |                          |                      |
    |                 |                       |      4. Return user      |                      |
    |                 |                       |      info or error       |                      |
    |                 |                       |<-------------------------|                      |
    |                 |                       |                          |                      |
    |                 |                       | 5. If valid, create      |                      |
    |                 |                       | session                  |                      |
    |                 |                       |------------------------------------------>|    |
    |                 |                       |                          |                 |    |
    |                 |                       |                          |      6. Store   |    |
    |                 |                       |                          |      session    |    |
    |                 |                       |                          |      data       |    |
    |                 |                       |                          |<----------------|    |
    |                 |                       |                          |                      |
    |                 |      7. Return auth   |                          |                      |
    |                 |      result and token |                          |                      |
    |                 |<----------------------|                          |                      |
    |                 |                       |                          |                      |
    | 8. Display      |                       |                          |                      |
    | result          |                       |                          |                      |
    |<----------------|                       |                          |                      |
    |                 |                       |                          |                      |
    | 9. Access       |                       |                          |                      |
    | protected       |                       |                          |                      |
    | resource        |                       |                          |                      |
    |---------------->|                       |                          |                      |
    |                 | 10. Validate          |                          |                      |
    |                 | session token         |                          |                      |
    |                 |--------- ---------------------------------------->|                     |
    |                 |                       |                          |                      |
    |                 |                       |                          |      11. Validate   |
    |                 |                       |                          |      token          |
    |                 |                       |                          |      and permissions|
    |                 |                       |<---------------------------------------------------------|
    |                 |                       |                          |                      |
    | 12. Return      |                       |                          |                      |
    | protected       |                       |                          |                      |
    | resource        |                       |                          |                      |
    |<----------------|                       |                          |                      |
    |                 |                       |                          |                      |
```

## 9. Error Handling and Recovery Workflow

The following sequence diagram illustrates the error handling and recovery process:

```
+--------+       +------------+       +----------------+       +---------------+       +------------+
| Client |       | Request    |       | Error          |       | Logging       |       | Monitoring |
|        |       | Handler    |       | Handler        |       | Service       |       | Service    |
+--------+       +------------+       +----------------+       +---------------+       +------------+
    |                  |                     |                       |                      |
    | 1. API Request   |                     |                       |                      |
    |----------------->|                     |                       |                      |
    |                  |                     |                       |                      |
    |                  | 2. Process          |                       |                      |
    |                  | request             |                       |                      |
    |                  |----------------X    |                       |                      |
    |                  | (Exception occurs)  |                       |                      |
    |                  |                     |                       |                      |
    |                  | 3. Forward          |                       |                      |
    |                  | exception           |                       |                      |
    |                  |-------------------->|                       |                      |
    |                  |                     |                       |                      |
    |                  |                     | 4. Categorize         |                      |
    |                  |                     | exception             |                      |
    |                  |                     |-----------------X     |                      |
    |                  |                     |                       |                      |
    |                  |                     | 5. Log error          |                      |
    |                  |                     |---------------------->|                      |
    |                  |                     |                       |                      |
    |                  |                     |                       | 6. Store error       |
    |                  |                     |                       | details              |
    |                  |                     |                       |----------------------|
    |                  |                     |                       |                      |
    |                  |                     | 7. Check if           |                      |
    |                  |                     | recoverable           |                      |
    |                  |                     |---------------------->|                      |
    |                  |                     |                       |                      |
    |                  |                     |      8. Return        |                      |
    |                  |                     |      recovery options |                      |
    |                  |                     |<----------------------|                      |
    |                  |                     |                       |                      |
    |                  |                     | 9. Apply              |                      |
    |                  |                     | recovery strategy     |                      |
    |                  |                     |---------------------->|                      |
    |                  |                     |                       |                      |
    |                  |                     |      10. Return       |                      |
    |                  |                     |      recovery result  |                      |
    |                  |                     |<----------------------|                      |
    |                  |                     |                       |                      |
    |                  | 11. Return          |                       |                      |
    |                  | appropriate         |                       |                      |
    |                  | response            |                       |                      |
    |                  |<--------------------|                       |                      |
    |                  |                     |                       |                      |
    | 12. Display      |                     |                       |                      |
    | result to user   |                     |                       |                      |
    |<-----------------|                     |                       |                      |
    |                  |                     |                       |                      |
```

## 10. Project Data Synchronization Workflow

The following sequence diagram illustrates the project data synchronization process:

```
+--------+       +---------------+       +-------------+       +----------------+       +--------------+
| Client |       | Project       |       | Database    |       | File Storage   |       | Notification |
|        |       | Manager       |       | Service     |       | Service        |       | Service      |
+--------+       +---------------+       +-------------+       +----------------+       +--------------+
    |                   |                      |                      |                       |
    | 1. Update         |                      |                      |                       |
    | project data      |                      |                      |                       |
    |------------------>|                      |                      |                       |
    |                   |                      |                      |                       |
    |                   | 2. Validate          |                      |                       |
    |                   | changes              |                      |                       |
    |                   |-------------------X  |                      |                       |
    |                   |                      |                      |                       |
    |                   | 3. Save changes      |                      |                       |
    |                   | to database          |                      |                       |
    |                   |--------------------->|                      |                       |
    |                   |                      |                      |                       |
    |                   |                      | 4. Update            |                       |
    |                   |                      | database             |                       |
    |                   |                      |------------------X   |                       |
    |                   |                      |                      |                       |
    |                   |      5. Return       |                      |                       |
    |                   |      update status   |                      |                       |
    |                   |<---------------------|                      |                       |
    |                   |                      |                      |                       |
    |                   | 6. Save related      |                      |                       |
    |                   | files                |                      |                       |
    |                   |--------------------------------------------->|                     |
    |                   |                      |                      |                       |
    |                   |                      |                      | 7. Store files        |
    |                   |                      |                      |--------------X        |
    |                   |                      |                      |                       |
    |                   |                      |      8. Return       |                       |
    |                   |                      |      storage status  |                       |
    |                   |<---------------------------------------------|                     |
    |                   |                      |                      |                       |
    |                   | 9. Update            |                      |                       |
    |                   | synchronization      |                      |                       |
    |                   | status               |                      |                       |
    |                   |--------------------->|                      |                       |
    |                   |                      |                      |                       |
    |                   | 10. Notify           |                      |                       |
    |                   | interested parties   |                      |                       |
    |                   |-------------------------------------------------------------->|    |
    |                   |                      |                      |                  |    |
    |                   |                      |                      |                  |    |
    |                   |                      |                      |     11. Send     |    |
    |                   |                      |                      |     notifications|    |
    |                   |                      |                      |<-----------------|    |
    |                   |                      |                      |                       |
    | 12. Return        |                      |                      |                       |
    | update result     |                      |                      |                       |
    |<------------------|                      |                      |                       |
    |                   |                      |                      |                       |
```