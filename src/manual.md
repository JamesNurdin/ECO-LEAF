# User manual 

To Create a new simulation model the user should create a new file within the examples directory, 
within the file the user should import the necessary classes and methods from the necessary extendedLeaf files.
The user should then proceed to initialise the simulation variable from the simp.Environment() class.
Following this the user should define the applications, infrastructure, power sources and power domains.
The user may optionally may define any events they want to occur through the event domain.
Finally, the user should pass the power domains' run command through the simulation variable to execute run the simulation.

-optional displaying results