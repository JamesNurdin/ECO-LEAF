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

## Week 9
### 13th November