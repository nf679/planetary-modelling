from vpython import *
import numpy as np
from copy import *
import matplotlib.pyplot as p


# Function to find the area between two vectors
def areaKep(r1, r2):
    # Angle between two vectors (inputs r1 and r2)
    theta = acos(dot(r1, r2) / (mag(r1) * mag(r2)))

    # Area from two vector inputs (r1, r2) using calculated angle theta
    areaK = mag(r1) * mag(r2) * (theta / 2)

    return areaK


dt = 0.0001  # timestep
step = 1  # loop counter
maxstep = 50000
G = 1

# Select either the two object testing system or planetary system
planetOption = int(input("Enter 1 for testing two object binary system, 2 for planetary system with central body: "))

#  Define the star, planets and constants as arrays based on user input above

if planetOption == 1:
    massesArr = [10000, 10000]
    posArr = [vector(2, 0, 0), vector(-2, 0, 0)]
    velArr = [vector(0, 30, 0), vector(0, -30, 0)]

else:
    massesArr = [10000, 100, 20, 100, 80, 40]
    posArr = [vector(0, 0, 0), vector(-3, 0, 0), vector(-3.2, 0, 0), vector(1.5, 0, 0), vector(0, 7, 0),
              vector(0, -12, 0)]
    velArr = [vector(0, 0, 0), vector(0, 60, 0), vector(0, 77, 0), vector(0, -75, 0), vector(40, 0, 0),
              vector(-31, 0, 0)]

# Array of colours to assign to objects in system
colorArr = [vector(1, 1, 0), vector(0, 1, 0), vector(0, 0, 1), vector(1, 0.5, 0), vector(0, 1, 1), vector(1, 0, 1),
            vector(0.5, 0, 0.5), vector(0.5, 0.5, 0), vector(0.5, 0.5, 1)]

accArr = []
for i in range(len(massesArr)):
    accArr.append(vector(0, 0, 0))

posArrPlus1 = []
for i in range(len(massesArr)):
    posArrPlus1.append(vector(0, 0, 0))

initialVelArr = deepcopy(velArr)

# Check if the input arrays aren't the same length
if len(massesArr) != len(posArr) or len(massesArr) != len(velArr):
    # If they are not of the same length print error
    print("Input arrays need to be of equal length")

    # Set step=maxstep to stop the main while loop running
    step = maxstep + 1

# Check if the length of the colour array has at least as many elements as the number of objects
if len(colorArr) < len(massesArr):
    # Print an error
    print("You need at least the number of colors in the colorArr as there are objects in system")

    # Set step=maxstep to stop the main while loop running
    step = maxstep + 1

# Define vPython objects for each object
for i in range(len(massesArr)):
    Name = "Ob" + str(i)
    Color = "color." + str(colorArr[i])
    vars()[Name] = sphere(pos=posArr[i], radius=0.00004 * massesArr[i], color=colorArr[i])

# Create a curve to follow each object as it moves
for i in range(len(massesArr)):
    Name = "trace" + str(i)
    obC = "Ob" + str(i)
    vars()[Name] = curve(radius=0.005, color=vars()[obC].color)

### Initialise arrays for the keppler area calculations

# Create an empty array for the vector from the central body to the object
radInitArr = []

# Empty array that will be filled with arrays for the areas of each object
areaArrays = []

# Empty array that will be filled with arrays for the areas of each object for small step (running total array)
areaRunTotArrays = []

# Center of Mass - Create an empty array for the vector from the central body to the object
radInitArrCM = []

# Center of Mass - Empty array that will be filled with arrays for the areas of each object
areaArraysCM = []

# Center of Mass - Empty array that will be filled with arrays for the areas of each object for small step (running total array)
areaRunTotArraysCM = []

# Initial vector to the center of mass
centerMassRunTot = vector(0, 0, 0)

for i in range(len(massesArr)):
    # Sun the masses times the displacement of each object from (0,0,0) to calculate the center of mass
    centerMassRunTot = centerMassRunTot + (massesArr[i] * posArr[i])

# Define an initial center of mass for the system
centerMass = centerMassRunTot * (1 / np.sum(massesArr))

for i in range(len(massesArr) - 1):
    # Append the vector from the first object to each body (except first) to the array of vectors:
    radInitArr.append(posArr[i + 1] - posArr[0])

    # Append the vector from center of mass to each body (except first) to the array of vectors:
    radInitArrCM.append(posArr[i + 1] - centerMass)

    # Create an empty array in the areaArrays for each object except first one
    areaArrays.append([])

    # Create an empty array of running totals for each object except first for running totals
    areaRunTotArrays.append([])

    # Create an empty array in the areaArraysCM for each object except first one
    areaArraysCM.append([])

    # Create an empty array of running totals for each object except first for running totals cemter of mass
    areaRunTotArraysCM.append([])

### Initial values for the angle between graph, used to calculate retrograde motion

# Create an array that will store the time differenece for the measurements for the above array
angleBetTime = [dt]

# Define reference axis to get angle the above vector is displaced by
refVec = vector(1, 0, 0)

# Empty array for object 1 to other objects
rOb1toOb = []

# emty array for angle between object 1 and other abject
angleBet1And = []

# Fill array with vectors between object 1 and every other object (except large central)
for i in range(len(massesArr) - 2):
    rOb1toOb.append(posArr[i + 2] - posArr[1])

# Fill array with angle between vector between Ob1 and ObN and the reference vector
for i in range(len(massesArr) - 2):
    angleBet1And.append([diff_angle(rOb1toOb[i], refVec)])

### Main loop

while step <= maxstep:

    rate(100)  # slow down the animation

    # Loop to make an array of all the future positions based on current velocities position and acceleration
    # This is because for acceleration+1 and velocity+1 both current location and location after time increment are needed.
    for i in range(len(posArrPlus1)):
        # Define the initial values of everything from the arrays
        ri = posArr[i]
        vi = velArr[i]
        ai = accArr[i]

        # find r i + 1
        riPlus1 = ri + (vi * dt) + (0.5 * ai * dt ** 2)

        # Add to the posArrPlus1 array
        posArrPlus1[i] = riPlus1

    arrayIndex = 0

    for i in range(len(massesArr)):

        # Deep copy the arrays that will be popped in the net step
        massesForIter = deepcopy(massesArr)
        posForIter = deepcopy(posArr)
        posArrPlus1ForIter = deepcopy(posArrPlus1)

        # Define the initial values of everything from the arrays
        ri = posForIter[arrayIndex]
        vi = velArr[arrayIndex]
        ai = accArr[arrayIndex]

        # Initial for aiplusone vector
        aiPlus1 = vector(0, 0, 0)

        # Remove the current mass velocity and position from an array
        # ie create an array of the values that will effec the current
        massesForIter.pop(arrayIndex)
        posForIter.pop(arrayIndex)
        posArrPlus1ForIter.pop(arrayIndex)

        # loop for all in the shortened arrays
        # i.e. the number of other objects in the system
        for i in range(len(massesForIter)):
            # Find the vector displacement between two objects
            # I.e. the vector between the current object at time i+1 and the other object at i+1
            r1to2Plus1 = posArrPlus1[arrayIndex] - posArrPlus1ForIter[i]

            # Find magnitude of this array vector
            magR1to2 = mag(r1to2Plus1)

            # Find a unit vector in this direction
            unitR1to2 = r1to2Plus1 / magR1to2

            # Find the acceleration after the timestep
            aiPlus1 = aiPlus1 + (-G * massesForIter[i] * unitR1to2) / (magR1to2 ** 2)

        # Ajust the velocity based on this timestep
        viPlus1 = vi + 0.5 * (ai + aiPlus1) * dt

        # Update the position and velocity vectors caclulated in previous loop for this array index
        # Have an array of the posiitons to append after all the final positions have been calculated
        velArr[arrayIndex] = viPlus1
        accArr[arrayIndex] = aiPlus1

        # Increace array index
        arrayIndex += 1

    # Update the general position array after all positions calculated
    posArr = deepcopy(posArrPlus1)

    ### Update data array for the angle between objects

    # Calculating vector between Ob 1 and the other objects (bearing in mind all objects have a 0 z position)
    for i in range(len(massesArr) - 2):
        rOb1toOb[i] = posArr[i + 2] - posArr[1]

    # Fill array with angle between vector between Ob1 and ObN and the reference vector
    for i in range(len(massesArr) - 2):
        angleBet1And[i].append(diff_angle(rOb1toOb[i], refVec))

    # Append a timestep to the end of the time reference array (the last element in the array + dt)
    angleBetTime.append(angleBetTime[-1] + dt)

    # Update the position of the visual objects
    for i in range(len(massesArr)):
        Name = "Ob" + str(i)
        vars()[Name].pos = posArr[i]

    # Update trace to follow planets positions for every iteration
    for i in range(len(massesArr)):
        tr = "trace" + str(i)
        Name = "Ob" + str(i)
        vars()[tr].append(vars()[Name].pos)

    # Increace count step
    step += 1

    # for every nth step (where remainder is 0)
    # Caclulated from current planet position and last planet position
    if step % 10 == 0:

        for i in range(len(massesArr) - 1):

            # Calculate current vector between object 1 and current object
            currentVec = posArr[i + 1] - posArr[0]

            # Add to a running total the area between this vector and last (from center of frame (0,0,0))
            areaRunTotArrays[i].append(areaKep(radInitArr[i], currentVec))

            # Reset the intiial vector to this vector
            radInitArr[i] = currentVec

            # Initial vector to the center of mass
            centerMassRunTot = vector(0, 0, 0)

            for n in range(len(massesArr)):
                # Sun the masses times the displacement of each object from (0,0,0) to calculate the center of mass
                centerMassRunTot = centerMassRunTot + (massesArr[n] * posArr[n])

            # Define a current center of mass for the system
            centerMassCurrent = centerMassRunTot * (1 / np.sum(massesArr))

            # Current vector between object and center of mass
            currentVecCM = posArr[i + 1] - centerMassCurrent

            # Append the care to the running totals for center of mass
            areaRunTotArraysCM[i].append(areaKep(radInitArrCM[i], currentVecCM))

            # Reset the initial CM vector to this center of mass vector
            radInitArrCM[i] = currentVecCM

    # For every nth step append current running total to array of areas
    if step % 100 == 0:

        for i in range(len(massesArr) - 1):
            # Appaend current value of area to array of areas
            areaArrays[i].append(np.sum(areaRunTotArrays[i]))

            # Reset the running total to 0
            areaRunTotArrays[i] = []

            # Appaend current value of area to array of areas Center of Mass
            areaArraysCM[i].append(np.sum(areaRunTotArraysCM[i]))

            # Reset the running total to 0 Center of mass
            areaRunTotArraysCM[i] = []

    if step % 1000 == 0:
        print("Current step", step)

# Initial vector to the center of mass
centerMassRunTot = vector(0, 0, 0)

for n in range(len(massesArr)):
    # Sun the masses times the displacement of each object from (0,0,0) to calculate the center of mass
    centerMassRunTot = centerMassRunTot + (massesArr[n] * posArr[n])

# Define a current center of mass for the system
centerMassCurrent = centerMassRunTot * (1 / np.sum(massesArr))

# Print area outputs for all relevant planets
for i in range(len(massesArr) - 1):
    print("\n")
    print("-----------------------------------------------------------------------------")
    print("\n")

    print("Ob", str(i + 1))
    print("\n")
    # print("areaArrays", areaArrays)

    # print("Area array", str(i+1), vars()[areaArrIter])
    print("Max difference area array between Ob", str(i + 1), "and Ob0            ",
          max(areaArrays[i]) - min(areaArrays[i]))
    # print("Numpy mean", str(i+1), np.mean(vars()[areaArrIter]))
    # print("Area array", str(i+1), "- numpy mean", str(i+1), vars()[areaArrIter] - np.mean(vars()[areaArrIter]))
    print("Standard deviation for Ob", str(i + 1), "and Ob0                       ",
          np.std(areaArrays[i] - np.mean(areaArrays[i])))

    print("\n")

    print("Max difference area array between Ob", str(i + 1), "and CM             ",
          max(areaArraysCM[i]) - min(areaArraysCM[i]))
    print("Standard deviation for Ob", str(i + 1), "and CM                        ",
          np.std(areaArraysCM[i] - np.mean(areaArraysCM[i])))

    Ob0R = mag(posArr[i + 1] - posArr[0])
    Ob0T = (2 * pi * Ob0R) / mag(velArr[i + 1])

    print("\n")
    # print("Final magnitude of angular velocity for OB", str(i+1), "about OB0    ", (mag(velArr[i+1]))/Ob0R)
    print("Final period for OB", str(i + 1), "about OB0                           ", Ob0T)
    print("Final R^3/T^2 for OB", str(i + 1), "about OB0                          ", Ob0R ** 3 / Ob0T ** 2)

    CMR = mag(posArr[i + 1] - centerMassCurrent)
    CMT = (2 * pi * CMR) / mag(velArr[i + 1])

    print("\n")
    # print("Final magnitude of angular velocity for OB", str(i+1), "about CM     ", (mag(velArr[i+1]))/CMR)
    print("Final period for OB", str(i + 1), "about CM                            ", CMT)
    print("Final R^3/T^2 for OB", str(i + 1), "about CM                           ", CMR ** 3 / CMT ** 2)

    print("\n")
    print("Change in velocity                                        ", mag(velArr[i + 1]) - mag(initialVelArr[i + 1]))

## Plotting the graph

# only run the graph for planetary system

if planetOption != 1:

    # Set inpout variables for plotting of the graph
    x = angleBetTime

    countSubplot = len(massesArr) - 2

    for i in range(len(massesArr) - 2):
        y1 = angleBet1And[i]

        keyLabel = "Angle 1 to " + str(i + 2) + "(rad)"

        # Plot both the values for the angles between 1 and 2 and the
        # p.plot(x,y1,linestyle='-',label=keyLabel,linewidth=0.5)

        p.subplot(countSubplot, 1, i + 1)
        p.plot(x, y1, linestyle='-', linewidth=0.5)
        p.grid(linestyle='dotted')
        p.ylabel(keyLabel)

    p.xlabel('dt (s)')
    # p.ylabel('Angle between planet and arbitary vector (1,0,0) (rad)')

    p.legend(loc='lower right')

    p.show()

print("\n\nend of program\n\n")
