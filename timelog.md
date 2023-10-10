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
* *2 Hours* Inital research and exploring into the background for the accurate example; idea will be a local content distribution network, in particular the idea works around "users" requesting data from these cache sites throughout the day with peaks occuring towards the evening
### 9th October 2023
* *2 Hours* Started planning on a potential working example by determining the infrastructure of the network, in particular it will have three main caches that will hold data which are all connected to a main database, there will be a set amount of users who are wirelessly connected to each node that will request and recieve data wirelessly 
* *4.5 Hours* Worked on creating the infrastructure for the example, plan is for tomorrow to finish off the application and placement strategy for the tasks. It should work by randomly assigning an application to a work station and then a request should be sent from the workstation to a cache which "determines" if the data requestsed is present, if not then the request should be furthered to the cloud where the result should then be returned to the user