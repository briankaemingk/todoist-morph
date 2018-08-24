# todoist-morph  [![Code Climate](https://codeclimate.com/github/briankaemingk/todoist-morph/badges/gpa.svg)](https://codeclimate.com/github/briankaemingk/todoist-morph)
Enhancements to native behavior in todoist to improve motivation, focus, and flow.

## Improve Focus

### Just-In-Time Tasking
If you use todoist as your trusted system, then you inevitably have hundreds of tasks in your backlog at a given moment. How do you decide which of these tasks to do at a particular moment? 

JIT Tasking automates backlog filtering to only reveal tasks at the precise time, location, and context when they are actionable.

### Useage

JIT Tasking only shows you tasks when you are able to complete them. It accomplishes this through a combination of filtering and todoist api changes that run in the background.

1. Add a task scheduled for a particular day and time that you need to complete on that day, but aren't able to do them until a certain time. For example, let's say you need to make a personal phone call, but you don't want to make the call until after your shift at work ends at 6PM. Add that task in Todoist as `Call dad about birthday party` and set the due date as `today 6pm`.

2. Instead of looking at the default Today view in Todoist, look at a filter you will create called `Todo (Level 1)` which will hide this time-specific task until 6PM when you are able to do it. TODO: Automate filter creation

3. When 6PM rolls around, the due date for the task will be automatically changed to all-day today, and the task will automatically appear in your `Todo (Level 1)` filter.

## Improve Motivation -- Implemented but currently not integrated

TODO: Integrate the below functionality

An automation to enable habit tracking in todoist. 

It integrates Seinfield's "[Don't Break the Chain](https://lifehacker.com/281626/jerry-seinfelds-productivity-secret)" method into [todoist](http://todoist.com/). Once it's setup, you can forget about it and it works seamlessly.

This is a different flavor of the originally implemented [habitist](https://github.com/amitness/habitist). While habitist is focused on daily habits, habitist (streak) can be applied to habits of any recurrence time-frames (daily, weekly, monthly, etc).

## Useage

1. You add habits you want to form as task on todoist with a recurring schedule (could be any recurrence pattern (`every day`, `every week` or `every year`, for example)

2. Add `[streak 0]` to the task

3. When you complete the task, the `[streak 0]` will become `[streak 1]`

4. If you fail to complete the task and it becomes overdue, the script will schedule it to today and reset `[streak X]` to `[streak 0]`.

## Installation

1. Fork and clone the repo
    ```
    git clone https://github.com/yourgithubusername/todoist-morph
    ```
2. Create a heroku app.
    ```
    heroku create appname
    ```
3. Set environment variable with your todost API key. You'll find API key under `Settings > Integrations` on [todoist.com](https://todoist.com).
    ```
     heroku config:set TODOIST_APIKEY='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    ``` 

4. Push the app
    ```
    git push heroku master
    ```
 
5. On [IFTTT](http://ifttt.com/), [create](https://ifttt.com/create) a new applet. 
    - On THIS, select datetime > 'Every Hour At' > ':00' 
    - On THAT, select Webhooks > Make a web request
    - Set URL to your heroku app URL:
    ```
    https://your-todoist-morph-app-name.herokuapp.com/
    ```
    - Set METHOD to GET
    - Hit Create Action
    - If you want this app to run more frequently than once an hour, at a maximum of ever 15 minutes, then repeat the above steps, creating applets that run at `:15` and `:30` and `:45` minutes past the hour.
    
6. Create the `Todo (Level 1) filter` in Todoist
    - Open Todoist and create a new filter 
    - In NAME, enter `Todo (Level 1)`
    - In QUERY, enter `due after: tod 23:59 & due before: tom 00:00`

7. Add a task to test it out. See the [Just-In-Time Tasking](#just-in-time-tasking) useage section for ideas.
    
 [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
