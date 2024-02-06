# Timelog

* Carbon Emissions Estimation in Edge Cloud Computing Simulations
* James Nurdin
* 2570809n
* Lauritz Thamsen 

## Guidance

* This file contains the time log for your project. It will be submitted along with your final dissertation.
* **YOU MUST KEEP THIS UP TO DATE AND UNDER VERSION CONTROL.**
* This timelog should be filled out honestly, regularly (daily) and accurately. It is for *your* benefit.
* Follow the structure provided, grouping time by weeks.  Quantise time to the half hour.

## Week 1
### 15 Sep 2023
* *0.5 Hours* Initial email interaction with Lauritz confirming an initial meeting of the 28th and arranging subsequent meetings moving onwards, received an initial collection of material to cover prior to the meeting on the 27th

## Week 2 
### 18th September 2023
* *0.5 Hours* Initial quick reading of project guidance notes in preparation for online meeting on the 21st
* *1 Hour* Creation of GitLab repository and uploading of the project template to the repo 
* *1 Hour* Installing and setup of necessary LaTeX files
### 19th September 2023
* *0.5 Hours* Resolved issues regarding the status file and building the pdf file.
* *1.5 Hours* Watched Wim Vanderbauwhede's talk on "Low carbon computing: Context, vision and challenges"
* *1.5 Hours* Watched Lauritz Thamsen's talk on "Scheduling and Placement for Low-Carbon Edge/Cloud Computing"
### 20th September 2023
* *1 Hour* Watched Noman Bashir's talk on Ecovisor: A Virtual Energy System for Carbon-Efficient Applications
* *1 Hour* Read and highlighted LEAF: Simulating Large Energy-Aware Fog Computing Environments
### 21st September 2023
* *1 Hour* Read and highlighted Cucumber: Renewable-Aware Admission Control for Delay-Tolerant Cloud and Edge Workloads 
* *2 Hours* Attended Project Meeting for level 4 Students
* *1 Hour*  Read and highlighted Towards a Staging Environment for the Internet of Things

## Week 3

### 26th September 2023
* *1.5 Hours* Gone through the CIT Service talk presentation
* *1 Hour* Downloaded both versions of LEAF in preparation for tomorrow's initial meeting and arranged some initial questions
### 27th September 2023
* *1 Hour* Attended the first supervisor meeting with Laurtiz and updated the minutes log on Moodle
### 29th September 2023
* *2 Hours* Explored the current version of LEAF and attempted an initial version of my own example in preparation for the meeting next Wednesday, explored using the carbon intensity API to retrieve real time carbon intensities and to calculate a carbon emission using the grid 
### 30th October 2023
* *1 Hour* Read and highlighted the email document sent from Lauritz and the relevant sections
### 1st October 2023
* *1.5 Hours* Continued on with exploring the LEAF architecture and finished working on my own example using the two provided ones for help, in particular created two linked nodes so far with power monitors between them, plan to create a custom application that uses these nodes as a source and sink.
* *1 Hour* changed the model to reflect a more advanced infrastructure and application, also introduced error catchment when pulling national grid carbon intensities
### 2nd October 2023
* *1 Hour* Started on the presentation for Lauritz to show progress of this week's work, also showing him my understanding of the LEAF API, in preparation I also went over the LEAF paper and API
* *0.5 Hours* Planned a quick timeline to how the following weeks should proceed as
### 3rd October 2023
* *1.5 Hours* Finished the PowerPoint presentation in preparation for the meeting tomorrow, sent it to Lauritz to review beforehand along with the custom example that was worked on.
### 4th October 2023
* *1 Hour* Met with Lauritz and presented the PowerPoint demonstrating the work done, discussed the work to get done by next meeting and concluded that the PowerPoints aren't needed and shouldn't be prioritised but can be used during meetings to help workflow. In addition to this recorded the minutes and updated the respective moodle page.
### 7th October 2023
* *3 Hours* Researched three valid data sets for the three main power sources that will be used to reference potential power models in the project, the three are the UK power grid, Ireland's offshore wind generation and a various sites of London with solar energy readings.  
### 8th October 2023
* *2 Hours* Initial research and exploring into the background for the accurate example; idea will be a local content distribution network, in particular the idea works around "users" sending data to these cache sites throughout the day with peaks occurring towards the evening

## Week 4
### 9th October 2023
* *2 Hours* Started planning on a potential working example by determining the infrastructure of the network, in particular it will have various caches that will allow for data to be stored into locally, there will be a probability associated if these caches can store data if it fails to do so (indicating that the cache is full) it will move to the next until finally storing the data to the cloud
* *4.5 Hours* Worked on creating the infrastructure for the example, plan is for tomorrow to finish off the application and placement strategy for the tasks. It should work by randomly assigning an application to a work station and then a submission should be sent from the workstation to a cache which "determines" if the data can be stored, if not then the request should be furthered to the cloud where the result should then be returned to the user.
### 10th October 2023
* *5 Hours* Had to spend most of the day trying to get the application which I created today to work with the infrastructure from yesterday, had an issue with connecting the app to the infrastructure, after a closer inspection the issue came from the Orchestrator class being needed to place the app onto the infrastructure. Finally, got it working with some tweaks.
### 11th October 2023
* *1 Hour* Had the weekly meeting with Lauritz and planned on what to do before the next meeting, this week I am going to be going over some more datasets and again refining the example so that this time the context is a little less exact and more justifiable, in addition to this I will also be working on starting the extended version of LEAF. 
### 14th October 2023
* *2 Hours* Went through the provided paper on federated learning and started planning the rework to the example
### 15th October 2023
* *2.5 Hours* Started work on the latest example in which there are two main classes of user infrastructure nodes, based on the FedZero paper provided by Lauritz they are single and multi users (silos) where multi-users have a power consumption and processing power of multiple users, before working on more I also retrieved some data from solcast to check that I was able to and was able to download 5 years of solar data for Glasgow, this is not what I will use just more rather a test 

## Week 5
### 17th October 2023
* *5 Hours* Carried out work on the example in particular setting up the infrastructure of the example and working on the application, still need to iron out a few bugs
### 19th October 2023
* *0.5 Hours* Sent off the email updating Lauritz on the progress made this week, received an email back with him mentioning and to read the paper: https://www.acm.org/publications/policies/artifact-review-badging to familiarise myself with how the ACM define repeatability, reproducibility, and replicability. Besides that I will continue on with the work set out. 
### 22nd October 2023
* *0.5 Hours* Read the ACM document titled Artifact Review and Badging following Lauritz's suggestion for repeating experiments 
* *1.5 Hours* Fixed a bug with the cluster power model not updating properly
* *2 Hours* Started work on movement of clients and the application of processes 

## week 6
### 23rd October 2023
* *1.5 Hour* Continued work implementing mobility to clients
### 24th October 2023
* *2 Hours* Continued working with the mobility of clients, instead of a path for the moment clients are placed randomly on the graph and stay there for the time being, I am having issues with the application of cluster clients and placing the application after each iteration
* *4 Hours* Took a break from the example and started work on the extended leaf application, in particular articulated how the extension of power sources could theoretically work, will wait till tomorrow and get Lauritz's thoughts towards it before fully starting on it 
### 25th October 2023
* *1 Hour* Had the weekly meeting with Lauritz and updated the weekly minutes for the meeting, main goal is to focus on the extended Leaf project
### 28th October 2023
* *3 Hours* Continued work for Extended Leaf, fully implemented the Solar power subclass

## Week 7
### 30th October 2023
* *3 Hours* Started work on the implemented the Wind power subclass
### 31st October 2023
* *2 Hours* Imported the National grid carbon intensity data and created the grid power type
* *3.5 Hours* implemented the power manager subclass, this class will be used to run the power sources that will capture the carbon intensity at each time frame and will coordinate with the power meters to derive a final estimated carbon emission
### 1st November
* *2 Hours* Renamed the PowerManager class to PowerDomain, along with this followed Lauritz's advice and looked through NOSE and discrete event simulation to refresh my understanding to allow for times of data changes in  the available power and carbon intensity to be implemented in the environment queue
### 3rd November
* *2.5 Hours* Had to rework the PowerDomain subclass in its entirety to ensure that it could allow for multiple power sources to be held in the datatype, in particular most of the logic that wasn't specific to the power source typeclasses
### 5th November
* *3 Hours* Fixed a bug concerning the environment running the processes. For some reason that simulation was running infinitely when the power domain had all the logic about the power sources. The reason for this was due to the fact that the environment that was calling the timeout method was not the same one used throughout the rest of the demo, along with this the timeout method was using an update of 0 seconds which meant that the environment time was not updating during the while loop because no increments of time were actually occurring.

## Week 8
### 6th November
* *2 Hours* Finished off the PowerDomain run process accounting for discrete updates to time, in particular each associated power source will have their correct updates occur only when needed, rather than updating the respective available power or carbon intensity "every second" the update correctly occurs
* *3 Hours* Started implementing the change that will assign nodes to different power sources rather than using just one, at the moment I am struggling in a discrete manner to move nodes that reside in a lower priority to a higher one when excess power becomes available during an update
### 7th November
* *2.5 Hours* After thinking about it properly the problem was resolved by considering the priority of the power sources, having a quantifying value to determine importance, any power source which is updated needs to check three kinds of nodes: 1st nodes its currently powering this ensures they are still running, 2nd would be unpowered nodes as they are the next important and a basis for raising errors during runtime as all nodes need tobe powered, 3rd and finally nodes that are currently being run by power sources with a lower priority as we ultimately want to always use the better power source these should be chosen first.
### 8th November
* *1 Hour* Had the meeting with Lauritz, we discussed the current state of the project and how to deal with the supposed infinite power situation, after this the meeting minutes was recorded and uploaded to moodle indicating the work needed to be done over the upcoming week, besides the rework with the infinite power situation the recording of the carbon intensity needs to be done along with the example.
### 9th November
* *2.5 Hours* To rework the infinite power situation I considered a discrete event updating and just leaving the unpowered nodes to remain turned off however this became problematic when dealing with larger examples and managing nodes, instead an enumerator class was created to determine if a power supply is renewable or not, then the logic to distribute power to the nodes at run time can still occur however we can just call a similar method without needing the total power generated by the source as it is assumed to be infinite 
### 10th November
* *1.5 Hour* Today the function for the function calculate the total carbon omitted was reworked to incorporate the changes necessary following yesterday's changes. In particular the work that has been done concerning the updating of the carbon intensity. In particular at every interval every power source will log there nodes current carbon intensity and current power reading for that interval, it works by having a dictionary every interval with the value containing a list of sub dictionaries describing the current situation for that power source, each value inside this dictionary is a nodes details containing, the power measurement, the carbon intensity and finally the source (might not be necessary considering that we are having a static priority)  
### 12th November
* *2 Hours* Introduced the priority system, it works by having the user decide on a positive integer value to determine the power source's priority, where the closer the value is to zero the higher the priority, at the moment this is necessary inorder to preserve the order of operations as the priority determines the index location of the power source, if Lauritz wants this changed I will do so, but only if he wants to. It works by leaving None spaces in between these spaces so that during runtime, if extra power sources want to be added they can be, however as discussed last week the logic to reorder the power sources will be left to the user's program logic.
* *0.5 Hours* Introduced the ability to remove nodes from the power manager

## Week 9
### 13th November
* *2.5 Hours* Introduced the ability to execute power manager commands during runtime execution. It operates through passing discrete events using pre-determined time stamps, a function the user wants to call and finally any necessary arguments. The aim of this feature will allow for external factors that should be considered outside the execution to be run without the need for the user to create and run their own "run" method, in particular the first application of this that comes to mind is adding and removing power nodes from the power domain.
### 14th November
* *1 Hour* Had to slightly rework the max power feature when reading a nodes load to determine if it is suitable for a given power source, in particular when trying to apply this to the larger examples I forgot to realise that nodes could either utilise a max power feature or a power per cu option, after looking through the framework the best solution is to just measure the power required for that node, in reality this more suitable due to the fact power consumption is not basing the load requirements on the max possible load but rather the actual consumption. After this had no issues applying the extended leaf the university example.
### 15th November
* *2.5 Hours* Continued work on the example, in particular as discussed a little while back the changing of the mobility and scenario of the example to reflect a city based one similar to the original smart city provided by LEAF, to dissociate mine with this one, the context has been reflected to represent Glasgow, to account for this, the flow of traffic has been researched to follow traffic distributions of Glasgow city center.
* *1 Hour* Had the meeting with Lauritz and spent some time updating the minutes page on moodle
### 16th November
* *1.5 Hours* Refactored the power source classes so that the file reader is now apart-of the abstract class due to it performing the same behaviour for all power sources, in addition to this included a specified encoder due to the fact that one of the cvs files had a Unicode byte order mark and was making accessing the headers more complicated than necessary.
### 18th November
* *0.5 Hours* Introduced a new enumerator for the power source called PowerLocation, this is used to specify the location of the power source in relation to the power domain, this has been included for the next feature which has been included which indicates whether more than one offsite non-renewable power source has been provided. This was due to the fact that Lauritz believed that having multiple offsite grids was unnecessary and in unrealistic which I agree with also.
* *2.5 Hours* Attempted to clean up the source code and reduce the overall complexity of the distributing of nodes. In particular, I have removed the multiple for loops as they were unnecessary. After spending some time evaluating ways to improve readability I found that the method iterates through all associated nodes (nodes associated to the power domain), previously I was iterating through subsets of the list based on if the nodes were powered: by the current power source, not powered, and powered by sources of lesser importance. Realistically I could just iterate through all the nodes and just use if statements to check for this, unfortunately I couldn't find another approach to carry out the logic so, it remains the same. 
### 19th November
* *1 Hour* Introduced annotated arguments for the priority, after trying to include this in the method call add_power_source I found out after researching that this was not possible and I would have to use comments instead, however this was unacceptable to me, instead I have used the attribute of the power source instead allowing it to occur. This has no impact to assign priority as this updates in runtime so can be used in the assignment beforehand.
* *0.5 Hours* After looking through the instance initialisation method I saw alot of code that was being repeated and not specific to each concrete class, so like the file reader I have introduced a super initialisation call and moved all non-specific attributes to the super class.

## Week 10
### 20th November 
* *2 Hours* Resolved the issue concerning the custom federated learning example getting the power domain to correctly output the carbon output, the issue stemmed from the fact that the env run process was asynchronous so was not finishing executing before the call to output the total carbon output. In addition to this reworked the power domain recording system so now, at every passing of 1 unit of time (in this context it is minutes) we record each associated power source's nodes' power usage, carbon intensity, power, carbon released. In addition, for the sake of making totalling easier whilst this is measured the power source's total carbon emission is calculated. The format for every time increment looks like this:                                   {power_source_name: {node_name: {power_usage: #, carbon_intensity: #, carbon_released: #}, carbon_released: #}} Where hashes represent values measured during runtime
* *1.5 Hours* Updated the file handler so that it is no longer static, using the super class changes made the other day, the method can now assign the power data directly inside the method, along with this the file paths are now changed to make choosing a file a little easier, now only the file name needs to be passed in rather than a filepath relative from the calling program file. In addition to this I have introduced a smart node distribution method where the method call to redistribute the nodes can be turned off, this has been done for examples where the change of power source is unnecessary for nodes and can make it easier to analyse the smart reshuffling of nodes later on, finally logger information has also been included to make it easier to digest what is happening at each section
* *1.5 Hour* Worked on producing smaller examples where some are based on the original versions but with the power domain and power sources included. In addition, to this I have included the original custom federated learning example where we have two versions of main, one with the "smart" power distribution and one without to show how it could theoretically work to show how the smarter version utilises the renewable power sources and has a smaller carbon emission. In addition to this started work on applying the framework to the custom smart city, in a means not to just copy the work the application context and nodes will be changed but as Lauritz gave me permission to base the examples movement on that of the smart city it will be a good demonstration to show how easy it is to apply the new framework to existing examples with minimal changes, the only change besides including a power domain and power source was changing a node to have a static power usage.
### 22nd November
* *2.5 Hours* Started work on the larger examples, in particular started working on a custom power type for this called BatteryPower, the goal with this will be able to power mobile nodes.
### 23rd November 
* *2 Hours* After spending some time trying to get this feature to work correctly, I have introduced a new class into the Power file, in particular the NodeDistributor, this is to move the logic of distributing nodes for a power source away from the power domain, in particular the role of this class is to allow the user to exactly define custom methods of distributing nodes after a discrete update event occurs for the power source. The class has two optional arguments to initialise it, the custom distribution method and a toggle for the smart distribution of nodes in the default method, the requirements of the custom method require that the method takes in as arguments of a power source and the list of associated nodes of the power domain. The reason this feature took so long to implement was due to the fact that the custom method I was passing through actually also passed through the self parameter as for testing purposes I took the default one and passed it through. 
* *0.5 Hours* After thinking about it carefully I believe I have come up with a set of 4 enumerations that should cover all the bases for a power source: Renewable, NonRenewable, Mixed and Battery. However, as I know Lauritz is uncertain about past choices I will get his opinion on the matter next week.
### 24th November 
* *1 Hour* Whilst thinking about ways to incorporate the battery I have introduced the ability to pause tasks and nodes, hopefully this will resolve issues about the battery without the need to remove nodes from the battery as ideally they should remain static. This works by introducing a new attribute to both node and task, which will cause a power measurement to return a 0 without unlinking the node from the power source
* *1 Hour* Fixed an issue that was causing events to be missed if the current time did not land directly on the update time, the fix for this was to introduce a new value in the event structure which kept track of events that were executed along with changing the check condition to accepts events that were in the past, with these two checks in place, if some form of catching up was needed i.e. an event was missed it can execute this task at the next chance it gets without having to worry about it being executed every iteration.
# 25th November 
* *1.5 Hours* After inspecting the carbon emissions, I relied on that the carbon intensity was higher than expected, after a closer look the issue stemmed from the fact that when I was logging the power usage I was treating the current value as a static value rather than a dynamic measurement in respect to the duration of which the node had been running for, to fix this I standardised the measure function by dividing it by 60 and multiplying it by the update interval, this would mean that for every env.timeout(1) then 1 minute has passed allowing for correct measurements of power, to allow the user easy access to this feature, I have also introduced a time conscious method in the node(power aware) class.

## Week 11
# 27th November 
* *0.5 Hours* Fixed some timing issues, first I moved the yield env.timeout method to the beginning of the whileloop as otherwise we were running the task immediately which is incorrect as the nodes would have just started, I also found that the simulation needs to run for 1 second extra otherwise the last update will not occur i.e. interval - 60 (1 hour) want to run for two hours -> run for (120 +1), now the trade-off in interval updates is that we loose the granularity with larger intervals and loose accuracy in results as the carbon intensity/ power available is not being updated as often.
* * 1 Hour* Resolved an issue with logging as due to the changes with the last change we now need to cast power used as a float now rather than in int, as because the actual power used was small compared to before, storing as an int was keeping the value at 0.
### 28th November
* *1 Hour* Spent a bit of time trying to improve the power file, in particular I tried messing around with associated nodes and the nodes_being powered lists as I wanted all nodes to be handled through the power domain but hold information about their current status in a private list in each power source class, I could not get this to work due to the fact that I will need to allow users to add custom classes.
* *1.5 Hours* I have changed the node distributor class to allow for a cleaner default method, in particular I have realised that np.inf will allow for mathematical operations and comparisons, because of this I can do away with the enumerations and just return np.inf in the get current power method of the grid, this should be okay as both me and Lauritz have allowed for the assumption that the power is infinite in the context of this framework, in addition to this I realised that the next update attribute is irrelevant now due to frequent changes made throughout development as the update interval and retrieve current power take into account the correct timings of the simulation through env.now() and the formatting to the timing of the files.
* *0.5 Hours* Included documentation into the classes and larger methods of Power.py
* *1.5 Hours* Now that the project is fairly expanded upon, I have relocated my own version of Extended LEAF to my project repository, had a few issues with modules not importing but all I had to do was include the src. extension to the imports and now they work without an issue.
### 29th November 
* *2 Hours* Introduced the ability to pause and unpause nodes for the user, in particular the proces works by considering the node distributor as static or dynamic, if the user wants a dynamic node distribution system all they need to do is pass the nodes through the power domain to allow for auto handling, if they want static nodes (nodes don't move) then they have to pass the nodes through the power sources, I have also created a default pause node distributor method which will just pause and unpause nodes based on power availability.
### 30th November
* *2.5 Hours* Properly started on the main example, after exchanges between Lauritz a few weeks back the main work on the example has been undertaken, currently the initial graph and power domains for the recharge points have been created, as previously stated the focus will be to avoid too much detail on the path and calculations of power on smart cars (this will be for the potential users of Extended LEAF) and more on showing the capabilities of the framework.
### 1st December
* *1.5 Hours* After initially testing the recharge points, I have noticed that with the static nodes the reference to the power nodes was missing during initialisation, so when nodes are passed through to the power source rather than the power domain, a link is created from the start rather than during the node distribution. After testing, I fixed an issue regarding this.
### 2nd December
* *2 Hours* Now that the locations of the nodes had been introduced last week, I have created a class for the RechargeStation (subclass of node), one aspect that took some time to fully realise was that the as a result of the main focus of extended leaf has been the power source and power domain managers the association has been one way between these and the nodes, as a result some time to find the optimal way to keep the focus towards the nodes for the example. The best approach found was to keep a reference to all power domains in the city class. An initial test running power domain run shows this is viable
### 3rd December
* *3.5 Hours* Started work on the powered Taxi, based on the logic of the original Taxi, this utilises power and needs to be considered, so far they have their initial battery power weighted towards being full, if below a threshold they will drive to a recharge station (source application), if not they just pass through, this is to avoid all taxis being used and can be reconfigured so a good amount stop to recharge.

## Week 12
### 4th December 
* *1.5 Hours* Continued work on the example in order to get the example to start calculating the expected carbon intensity in preparation before the meeting with Lauritz.
### 6th December 
* *1 Hour* Had the meeting with Lauritz and discussed the progress made this week along with what work was intended to be completed over the two-week meeting gap, in addition I informed him that I was going to take the 7th and 8th off to focus on an upcoming exam, but would continue afterwards. Also updated weekly meeting minutes.
### 9th December 
* *2 Hours* Started work on the test suite to ensure that the framework is correctly functioning now that all the core features are finished. Researched options and chose to go with unittest.
### 10th December 
* *3.5 Hours* Started the status report, to ensure that the project has a clear aim I, revisited the paper for LEAF to understand the initial motivations for that project then using the initial project description set out to write the first two parts of the project.

## Week 13
### 11th December
* *4 Hours* Finished off the status report ready for it to be submitted for tomorrow. In particular for the plan I thought carefully about the work I needed to get done and have decided to use the time over the holidays to heavily invest in the project ensuring that the framework is nearly finished by the start of semester 2.
### 12th December
* *2.5 Hours* Continued on with the unit tests, started implementing tests for the Solar power class.
* *5 Hours* Finished off unit tests for all the power sources.
### 14th December
* *7 Hours* Implemented remaining unit tests for the power domain and node distributor classes, some tests have been omitted based on the fact that they only carry out side effects and should be considered for the integration testing.
### 15th December
* *2 Hours* Reworked the framework to account for the inclusion of power consumed by data links.
* *0.5 Hours* Updated unit tests to reflect changes made to framework
* *2 Hours* Implemented the file writer along with the necessary validation and unit tests respectively.  
* *1.5 Hours* Reshuffled the work done recently, created a new file to handle file details along with creating a new directory for results every time the fileHandler class is created.
* *4.5 Hours* After getting the previous work done, a large road block has appeared with the plotly and kaleido packages, unfortunately despite countless hours trying to get the packages to work I am unable to get the write_image function to work. I will have to re-examine the problem later
### 16th December
* *2 Hours* Resolved the issue by installing an earlier version of kaleidoscope, apparently other people had the same problem but version 0.1.0.post1 resolved the issue.
* *3 Hours* Implemented a function that was capable of restructuring the captured data from the simulation, along with this worked on a graphing function that allows for graphs to be saved that take in an attribute and a list of entities and shows the time series 
### 17th December
* *2 Hours* Continued work on graphing function that allows the user to display the time series of results, allowing for a range of features to customise results.
* *2.5 Hours* Also introduced the ability to allow for the power domains to now be graphed, during which a bug appeared that caused simulations to extend into a new day i.e. any simulation that continued after 24:00:00 has been fixed.
* *1.5 Hour* Introduced the ability for batteries to now have their power recorded, this is to allow for the ability to graph data as while the data is recorded in respect to the nodes it is not for the power sources as the renewables are logged using the data from file and mixed power sources are assumed to be infinite.

## Week 14
### 18th December
* *3 Hours* Introduced the ability to aggregate figures into a single pdf, allowing for the ability to see results from a range of values
* *1 Hour* Carried out some research into a new type of example and have chosen to proceed with a precise agriculture example, where smart sensors help optimise farming, in addition to this planned out roughly core aspects and features
* *2 Hours* Made some changes to the file reader along with started work on the precise agriculture example.
### 19th December
* *1 Hour* Organised work that needs that has been completed, works that needs to be done and work that could be done.
* *2 Hours* Continued on with the precision agriculture example, in particular got the infrastructure started by allowing for plots to be constructed, where each plot is a rectangular grid with a node attached to the perimeter for the fog node.
* *3 Hours* Continued on with the infrastructure, created the core nodes and set up the power domains and necessary ground-work to apply the application tomorrow.
### 20th December
* *1 Hour* After working on a new small example before tomorrow's meeting, a bug was found due to the fact when a node is removed from the power domain, the power source still powering it is never notified and still thinks it's a part of the power domain, a fix has been made that removes the node from the power source and vice versa. 
* *2 Hours* Continued work on example by including the application and an initial full running and outputting of data to demo the features.
### 21st December
* *0.5 Hours* Carried out the meeting with Lauritz and discussed the submitted winter status report, in particular we discussed the need to ensure that enough time is kept to ensure that a quality final dissertation can be written along with the fact that Laurtiz wont be able to review the work too much, as discussed with Laurtiz I will have the next two weeks off to be fresh and ready for the start of the new semeseter. 

## Week 15
Holiday break

## Week 16
### 3rd January
* *1.5 Hours* Introduced a change to prepare for a new feature that will be added, the current state of the power is now held in the remaining_power field that needs to be updated every event, this will allow for the get_current_power to just call this method.
* *2.5 Hours* Following the previous change, in order to log the charging of the battery, a few new features have been added, first the ability to append to the captured data log, in addition to this a new dictionary has been added called log changes where events in the event queue that require data to be written to the captured data are temporarily stored here before the log is actually written to avoid key errors.
* *0.5 Hours* Fixed an issue due to the fact that the actual power sources when consuming power for an update event wasn't being saved to the current score
### 6th January
* *4.5 Hours* Implemented the ability that when a node is task at a point all data flows and tasks further on in the graph return 0 in addition to this
### 7th January
* *2 Hours* Changed the term entities to Powered Infrastructure to give more meaning to the items that are concrete implementations of the Power Model class. In addition to this went through and made some optimisation changes and resolved any issues that were preventing tests from passing.

## Week 17
### 9th January
* *2.5 Hours* Introduced a new example to demonstrate the pausing features of the framework, in addition to this fixed an issue with the pausing feature where the unpause method was being called repeatedly so have a check which saves the state, in addition included a new figure for the power meter.
* *2 Hours * On inspecting the figure it still appeared that power measurements were still recording subsequent readings as normal and not treating them as 0, the issue is due to the fact that the power meter for an application calls the task.measure() call, instead of trying again to work around it, I have introduced a new attribute for tasks keeping track of the application and then when a task is paused we can just traverse through entities and pause them.
### 11th January
* *2 Hours* Also introduced the ability for links to be paused and subsequent data flows associated.
### 12th January
* *2.5 Hours* Created a new small example called carbon aware orchestrator, the focus is the distribution of applications on optimal nodes, to do this a few changes needed to be made, in particular the orchestrator class now requires the power domain and the power meters are now able to measure readings while not placed on infrastructure to keep an accurate timeline. 
### 14th January
* *4 Hours* Continued work on the example by introducing the drone class along with generating a flight path and the ability to return back to the recharge station when under a threshold of power.

## Week 18
### 15th January
* *2.5 Hours* Introduced a new example demonstrating the ability to create a custom static powered infrastructure distributor for power sources. The intention might be for this is to allow users to change the focus for potentially allowing unpowered entities the ability to run if power is limited in a round-robin mentality. Also, re-worked how entities in the dynamic approach are handled after identifying a bug where they are now initially paused. 
* *1.5 Hours* Explored introducing a new approach to handling the node data when being captured akin to the power meter but the infrastructure requires the data to be easily accessible so was scrapped, also removed some unnecessary methods found
### 17th January
* *1 Hour* Reworked the events system into its own class allowing for events to be created in a clearer manner, also introduced the ability to repeat events after a certain amount of time 
* *3 Hours* Continued work on introducing new ideas as discussed where the goal for the next meeting is to produce and brainstorm new example ideas, finished with the small ones and introduced the idea of heuristics where nodes can have preferred power sources based on properties of either i.e. uncapped power nodes must be assigned to the grid.
### 19th January
* *2.5 Hours* Fixed mistake in event counters, moved the updating of power source to start of the discrete event and fixed an issue with the plotting of figures when a new day starts.
* *1 Hour* Introduced the last small example along with the necessary documentation to describe it.
### 20th January
* *1 Hour* Introduced the code for the second medium example along with the necessary documentation and explanation for it.
### 21st January
* *1.5 Hours* Continued work with document along with finishing the diagrams

## Week 19
### 23rd January
* *4.5 Hours* Introduced a new class called event domain that runs the events separately from the power domain, these are logged to the event domain event history that keeps track of which events have been called, from this we have also changed the figure plotter to allow for each event to be plotted correctly.
### 24th January
* *3.5 Hours* Made changes to the figure plotter now the figure plotter is its own class and the events occur on their own figure, this is to prevent the nodes being repeated on the legend and looks more presentable.
* *1 Hour* Carried out the changes to all existing examples to allow them to run, also moved the update interval back to the end of the while loop so all events and actions of the discrete event occur before the time updates.
### 25th January
* *3.5 Hours* Went through and fixed all the examples, also identified and fixed an issue with the dictionary with recorded results where the key being used for every time interval was the string version of the time and was being overwritten when simulations longer than 24 hours occurred, fix was to change to the env.now+start index instead as that is unique.
### 28th January
* *2.5 Hours* Introduced a visualiser for the simulation showing how nodes move between power sources.

## Week 20
### 29th January 
* *3 Hours* Continuing on with the animation, reworked it to allow for basic controls of the timeseries including a play/pause button along with a slider to quickly access specific points of time.
### 30th January
* *2 Hours* Went back and reworked the diagrams for the smaller examples to a higher quality by including the application that would lie on top of aspects of the infrastructure, also created a new class to allow for the debug print trace to remove irrelevant info.
### 31st January
* *1.5 Hours* Included improvements to the controls to the animation and playback controls along with including ticks on the slider.
* *1 Hour* Attempted to improve the x-axis tick terms.
* Things to do following this:
- go through examples and change to follow small4/medium 2
- fix issue with application and task allocation with source node for the drone
