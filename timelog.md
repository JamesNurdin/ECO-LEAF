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
* *0.5 Hours* Inital email interaction with Lauritz confirming an inital meeting of the 28th and arranging subsequent meetings moving onwards, recieved an inital collection of material to cover prior to the meeting on the 27th

## Week 2 
### 18th September 2023
* *0.5 Hours* Inital quick reading of project guidance notes in preperation for online meeting on the 21st
* *1 Hour* Creation of GitLab repoisitory and uploading of the project template to the repo 
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
* *1.5 Hours* Gone through the CIT Servicetalk presentation
* *1 Hour* Downloaded both versions of LEAF in preperation for tommorows intial meeting and arranged some inital questions
### 27th September 2023
* *1 Hour* Attended the first supervisor meeting with Laurtiz and updated the minutes log on Moodle
### 29th September 2023
* *2 Hours* Explored the current version of LEAF and attempted an inital version of my own example in preperation for the meeting next Wednesday, explored using the carbon intensity API to retreive real time carbon intensities and to calcualte a carbon emission using the grid 
### 30th October 2023
* *1 Hour* Read and highlighted the email document sent from Lauritz and the relevant sections
### 1st October 2023
* *1.5 Hours* Continued on with exploring the LEAF architecture and finished working on my own example using the two provided ones for help, in particular created two linked nodes so far with power monitors between them, plan to create a custom application that uses these nodes as a source and sink.
* *1 Hour* changed the model to reflect a more advanced infrastructure and application, also introduced error catchment when pulling national grid carbon intensities
### 2nd October 2023
* *1 Hour* Started on the presentation for Lauritz to show progress of this weeks work, also showing him my understanding of the LEAF API, in preperation I also went over the LEAF paper and API
* *0.5 Hours* Planned a quick timeline to how the following weeks should proceed as
### 3rd October 2023
* *1.5 Hours* Finished the powerpoint presentation in preparation for the meeting tomorrow, sent it to Lauritz to review beforehand along with the custom example that was worked on.
### 4th October 2023
* *1 Hour* Met with Lauritz and presented the PowerPoint demonstrating the work done, discussed the work to get done by next meeting and concluded that the PowerPoints aren't needed and shouldnt be prioritised but can be used during meetings to help workflow. In addition to this recorded the minutes and updated the respective moodle page.
### 7th October 2023
* *3 Hours* Researched three valid data sets for the three main power sources that will be used to reference potential power models in the project, the three are the UK power grid, Ireland's offshore wind generation and a various sites of London with solar energy readings.  
### 8th October 2023
* *2 Hours* Inital research and exploring into the background for the accurate example; idea will be a local content distribution network, in particular the idea works around "users" sending data to these cache sites throughout the day with peaks occuring towards the evening

## Week 4
### 9th October 2023
* *2 Hours* Started planning on a potential working example by determining the infrastructure of the network, in particular it will have various caches that will allow for data to be stored into locally, there will be a probability associated if these caches can store data if it fails to do so (indicating that the cache is full) it will move to the next until finally storing the data to the cloud
* *4.5 Hours* Worked on creating the infrastructure for the example, plan is for tomorrow to finish off the application and placement strategy for the tasks. It should work by randomly assigning an application to a work station and then a submission should be sent from the workstation to a cache which "determines" if the data can be stored, if not then the request should be furthered to the cloud where the result should then be returned to the user.
### 10th October 2023
* *5 Hours* Had to spend most of the day trying to get the application which I created today to work with the infrastructure from yesterday, had an issue with connecting the app to the infrastructure, after a closer inspection the issue came from the Orchestrator class being needed to place the app onto the infrastructure. Finaly got it working with some tweaks.
### 11th October 2023
* *1 Hour* Had the weekly meeting with Lauritz and planned on what to do before the next meeting, this week I am going to be going over some more datasets and again refining the example so that this time the context is a little less exact and more justifiable, in addition to this I will also be working on starting the extended version of LEAF. 
### 14th October 2023
* *2 Hours* Went through the provided paper on federated learning and started planning the rework to the example
### 15th October 2023
* *2.5 Hours* Started work on the latest example in which there are two main classes of user infrastructure nodes, based on the FedZero paper provided by Lauritz they are single and multi users (silos) where multiusers have a power consumption and processing power of multiple users, before working on more I also retrieved some data from solcast to check that I was able to and was able to download 5 years of solar data for Glasgow, this is not what I will use just more rather a test 

## Week 5
### 17th October 2023
* *5 Hours* Carried out work on the example in particular setting up the infrastructure of the example and working on the application, still need to iron out a few bugs
### 19th October 2023
* *0.5 Hours* Sent off the emal updating Lauritz on the progress made this week, recieved an email back with him mentioning and to read the paper: https://www.acm.org/publications/policies/artifact-review-badging to familiarise myself with how the ACM define repeatability, reproducibility, and replicability. Besides that I will continue on with the work set out. 
### 22nd October 2023
* *0.5 Hours* Read the ACM document titled Artifact Review and Badging following Lauritz's suggestion for repeating experiments 
* *1.5 Hours* Fixed a bug with the cluster power model not updating properly
* *2 Hours* Started work on movement of clients and the application of processes 

## week 6
### 23rd October 2023
* *1.5 Hour* Continued work implementing mobility to clients
### 24th October 2023
* *2 Hours* Continued working with the mobility of clients, instead of a path for the moment clients are placed randomly on the graph and stay there for the time being, I am having issues with the application of cluster clients and placing the application after each iteration
* *4 Hours* Took a break from the example and started work on the extended leaf application, in particular articulated how the extention of power sources could theortically work, will wait till tomorrow and get Lauritz's thoughts towards it before fully starting on it 
### 25th October 2023
* *1 Hour* Had the weekly meeting with Lauritz and updated the weekly minutes for the meeting, main goal is to focus on the extended Leaf project
### 28th October 2023
* *3 Hours* Continued work for Extended Leaf, fully implemented the Solarpower subclass

## Week 7
### 30th October 2023
* *3 Hours* Started work on the implemented the Windpower subclass
### 31st October 2023
* *2 Hours* Imported the National grid carbon intensity data and created the grid powertype
* *3.5 Hours* implemented the power manager subclass, this class will be used to run the power sources that will capture the carbon intensity at each time frame and will coordinate with the power meters to dervie a final estimated carbon emission
### 1st November
* *2 Hours* Renamed the PowerManager class to PowerDomain, along with this followed Lauritz's advice and looked through NOSE and discrete event simulation to refresh my understanding to allow for times of data changes in  the available power and carbon intensity to be implemented in the environment queue
### 3rd November
* *2.5 Hours* Had to rework the PowerDomain subclass in its entirety to ensure that it could allow for multiple power sources to be held in the datatype, in particular most of the logic that wasnt specific to the power source typeclasses
### 5th November
* *3 Hours* Fixed a bug concerning the enviroment running the processes. For some reason that simulation was running infintly when the power domain had all the logic about the power sources. The reason for this was due to the fact that the enviroment that was calling the timeout method was not the sameone used throughout the rest of the demo, along with this the timeout method was using an update of 0 seconds which meant that the enviornment time was not updating during the while loop because no increments of time were actually occuring.

## Week 8
### 6th November
* *2 Hours* Finished off the PowerDomain run process accounting for discrete updates to time, in particular each associated power source will have their correct updates occur only when needed, rather than updating the respective available power or carbon intensity "every second" the update correctly occurs
* *3 Hours* Started implementing the change that will assign nodes to different power sources rather than using just one, at the moment I am struggling in a discrete manner to move nodes that reside in a lower prioirty to a higher one when excess power becomes available during an update
### 7th November
* *2.5 Hours* After thinking about it properly the problem was resolved by considering the prioirty of the power sources, having a quantifying value to determine importance, any power source which is updated needs to check three kinds of nodes: 1st nodes its currently powering this ensures they are still running, 2nd would be unpowered nodes as they are the next important and a basis for raising errors during runtime as all nodes need tobe powered, 3rd and finally nodes that are currently being ran by power sources with a lower prioirty as we ultimatley want to always use the better power source these should be chosen first.
### 8th November
* *1 Hour* Had the meeting with Lauritz, we discussed the current state of the project and how to deal with the supposed infinite power situation, after this the meeting minutes was recorded and uploaded to moodle indicating the work needed to be done over the upcoming week, besides the rework with the infinite power situation the recording of the carbon intensisty needs to be done along with the example.
### 9th November
* *2.5 Hours* To rework the infinite power situation I considered a discrete event updating and just leaving the unpowered nodes to remain turned off however this became problematic when dealing with larger examples and managing nodes, instead a enumerator class was created to determine if a power supply is renewable or not, then the logic to distribute power to the nodes at run time can still occur however we can just call a similar method without needing the total power generated by the source as it is assumed to be infinite 
### 10th November
* *1.5 Hour* Today the function for the calculate the total carbon omitted was reworked to incorperate the changes necessary following yesterday's changes. In particular the work that has been done concerning the updating of the carbon intensity. In particular at every interval every power source will log there nodes current carbon intensity and current power reading for that interval, it works by having a dictionary every interval with the value containing a list of sub dictionaries describing the current sitation for that power source, each value inside this dictionary is a nodes details containing, the power measurement, the carbon intensity and finally the source (might not be necessary considering that we are having a static priority)  
### 12th November
* *2 Hours* Introduced the priority system, it works by having the user decide on a positive integer value to determine the power source's priority, where the closer the value is to zero the higher the priority, at the moment this is necessary inorder to preserve the order of operations as the prioirty determins the index location of the power source, if Lauritz wants this changed I will do so, but only if he wants to. It works by leaving None spaces in between these spaces so that during runtime, if extra power sources want to be added they can be, however as discussed last week the logic to reorder the power sources will be left to the user's program logic.
* *0.5 Hours* Introduced the ability to remove nodes from the power manager

## Week 9
### 13th November
* *2.5 Hours* Introduced the ability to execute power manager commands during runtime execution. It operates through passing discrete events using pre determined time stamps, a function the user wants to call and finally any necessary arguments. The aim of this feature will allow for external factors that should be considered outside of the execution to be ran without the need for the user to create and run their own "run" method, in particular the first application of this that comes to mind is adding and removing power nodes from the power domain.
### 14th November
* *1 Hour* Had to slightly rework the max power feature when reading a nodes load to determine if it is suitable for a given power source, in particular when trying to apply this to the larger examples I forgot to realise that nodes could either utilise a max power feature or a power per cu option, after looking through the framework the best solution is to just measure the power required for that node, in reality this more suitable due to the fact power consumption is not basising the load requirements on the max possible load but rather the actual consumption. After this had no issues applying the extended leaf the university example.
### 15th November
* *2.5 Hours* Continued work on the example, in particular as discussed a little while back the changing of the mobility and scenario of the example to reflect a city based one similar to the orignial smart city provided by LEAF, to disociate mine with this one, the context has been reflected to represent Glasgow, to account for this, the flow of traffic has been researched to follow traffic distributions of Glasgow city center.
* *1 Hour* Had the meeting with Lauritz and spent some time updatng the minutes page on moodle
### 16th November
* *1.5 Hours* Refactored the power source classes so that the file reader is now apart of the abstract class due to it performing the same behaviour for all power sources, in addition to this included a specified encoder due to the fact that one of the cvs files had a Unicode byte order mark and was making accessing the headers more complicated than necessary.
### 18th November
* *0.5 Hours* Introduced a new enumerator for the power source called PowerLocation, this is used to specify the location of the power source in relation to the power domain, this has been included for the next feature which has been included which indicates whether more than one offsite non renewable power source has been provided. This was due to the fact that Lauritz believed that having multiple offsite grids was unecessary and in unrealistic which I agree with also.
* *2.5 Hours* Attempted to clean up the source code and reduce the overall complexity of the distributing of nodes. In particular I have removed the multiple for loops as they were unecessary. After spending some time evaluating ways to improve readability I found that the method iterates through all associated nodes (nodes associated to the power domain), previously I was iterating through subsets of the list based on if the nodes were powered: by the current power source, not powered, and powered by sources of lesser importance. Realistically I could just iterate through all the nodes and just use if statements to check for this, unfortunatelly I couldnt find another approach to carry out the logic so it remains the same. 
### 19th November
* *1 Hour* Introduced annotated arguments for the priority, after trying to include this in the method call add_power_source I found out after researching that this was not possible and I would have to use comments instead, however this was unacceptable to me, instead I have used the attribute of the power source instead allowing it to occur. This has no impact to assign priority as this updates in runtime so can be used in the assignment beforehand.
* *0.5 Hours* After looking through the instance intialisation method I saw alot of code that was being repeated and not specific to each concrete class, so like the file reader I have introduced a super intialisation call and moved all non specific attributes to the super class.

## Week 10
### 20th November 
* *2 Hours* Resolved the issue concerning the custom federated learning example getting the power domain to correctly output the carbon output, the issue stemed from the fact that the env run process was asynchronous so was not finishing executing before the call to output the total carbon output. In addition to this reworked the power domain recording system so now, at every passing of 1 unit of time (in this context it is minutes) we record each associated power source's nodes' power usage, carbon intensity, power, carbon released. In addition for the sake of making totalling easier whilst this is measured the power source's total carbon emission is calculated. The format for every time increment looks like this:                                   {power_source_name: {node_name: {power_usage: #, carbon_intensity: #, carbon_released: #}, carbon_released: #}} Where hashes represent values measured during runtime
* *1.5 Hours* Updated the file handler so that it is no longer static, using the super class changes made the other day, the method can now assign the power data directly inside the method, along with this the file paths are now changed to make choosing a file a little bit easier, now only the file name needs to be passed in rather than a filepath relative from the calling program file. In addition to this I have introduced a smart node distribution method where the method call to redistribute the nodes can be turned off, this has been done for examples where the change of power source is unecessary for nodes and can make it easier to analyse the smart reshuffling of nodes later on, finally logger information has also been included to make it easier to digest what is happening at each section
* *1.5 Hour* Worked on producing smaller examples where some are based on the original versions but with the power domain and power sources included. In addition tothis I have included the original custom federated learning example where we have two versions of main, one with the "smart" power distribution and one without to show howit could theoretically work to show how the smarter version utilises the renewable power sources and has a smaller carbon emission. In addition to this started work on applying the framework to the custom smart city, in a means not to just copy the work the application context and nodes will be chenaged but as Lauritz gave me permission to base the examples movment on that of the smart city it will be a good demonstration to show how easy it is to apply the new framework to existing examples with minimal changes, the only change besides including a power domain and power source was changing a node to have a static power usage.
### 22nd November
* *2.5 Hours* Started work on the larger examples, in particular started working on a custom power type for this called BatteryPower, the goal with this will be able to power mobile nodes.
### 23rd November 
* *2 Hours* After spending some time trying to get this feature to work correctly, I have introduced a new class into the Power file, in particular the NodeDistributor, this is to move the logic of distributing nodes for a power source away from the power domain, in particular the role of this class is to allow the user to exactly define custom methods of distributing nodes after a dicrete update event occurs for the power source. The class has two optional arguments to intialise it, the custom distribution method and a toggle for the smart distribution of nodes in the default method, the requirements of the custom method require that the method takes in as arguments of a power source and the list of associated nodes of the power domain. The reason this feature took so long to implement was due to the fact that the custom method I was passing through actually also passed through the self parameter as for testing purposes I took the default one and passed it through. 
* *0.5 Hours* After thinking about it carefully I believe I have come up with a set of 4 enumerations that should cover all the bases for a power source: Renewable, NonRenewable, Mixed and Battery. However as I know Lauritz is uncertain about past choices I will get his opinion on the matter next week.
### 24th November 
* *1 Hour* Whilst thinking about ways to incorperate the battery I have introduced the ability to pause tasks and nodes, hopefully this will resolve issues about the battery without the need to remove nodes from the battery as ideally they should remain static. This works by introducing a new attribute to both node and task, which will cause a power measurement to return a 0 without unlinking the node from the power source
* *1 Hour* Fixed an issue that was causing events to be missed if the current time did not land directly on the update time, the fix for this was to introduce a new value in the event structure which kept track of events that were executed along with changing the check condition to accepts events that were in the past, with these two checks in place, if some form of catching up was needed i.e. an event was missed it can execute this task at the next chance it gets without having to worry about it being executed every iteration.
# 25th November 
* *1.5 Hours* After inspecting the carbon emissions, I realied that the carbon intensity was higher than expected, after a closer look the issue stemmed from the fact that when I was logging the power usage I was treating the current value as a static value rather than a dynamic measurement in respect to the duration of which the node had been running for, to fix this I standardised the measure function by dividing it by 60 and multiplying it by the update interval, this would mean that for every env.timeout(1) then 1 minute has passed allowing for correct measurements of power, to allowthe user easy access to this feature, I have also introduced a time concious method in the node(power aware) class.

## Week 11
# 27th November 
* *0.5 Hours* Fixed some timing issues, first I moved the yeild env.timeout method to the begining of the whileloop as otherwise we were running the task immediatley which is incorrect as the nodes would have just started, I also found that the simulation needs to run for 1 second extra otherwise the last update wont occur i.e. interval - 60 (1 hour) want to run for two hours -> run for (120 +1), now the trade off in interval updates is that we loose the granuality with larger intervals and loose accurasy in results as the carbon intensity/ power available is not being updated as often.
* * 1 Hour* Resolved an issue with logging as due to the changes with the last change we now need to cast power used as a float now rather than in int, as because the actual power used was small compared to before, storing as an int was keeping the value at 0.
### 28th November
* *1 Hour* Spent a bit of time trying to improve the power file, in particular I tried messing around with associated nodes and the nodes_being powered lists as I wanted all nodes to be handled through the power domain but hold information about their current status in a private list in each power source class, I could not get this to work due to the fact that I will need to allow users to add custom classes.
* *1.5 Hours* I have changed the node distributor class to allow for a cleaner default method, in particular I have realised that np.inf will allow for mathematical operations and comparisons, because of this I can do away with the enumerations and just return np.inf in the get current power method of the grid, this should be okay as both me and Lauritz have allowed for the assumption that the power is infinite in the context of this framework, in addition to this I realsied that the next update attribute is irrelevent now due to frequent changes made throughout development as the update interval and retrieve current power take into account the correct timings of the simulation through env.now and the formatting to the timing of the files.

TODO:
Main example
Check Battery, in particular allow for managing of nodes and the reading of data from file(just want update intervals for the battery could retreive the headers where data would be header [1])