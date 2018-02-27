import numpy as np
import time, os

## Initial configurations
finalBreak     = 8*60*60
numVars        = 500
outputFilename = 'output.dat'


## Actual script
outputFile = open( outputFilename, 'w', 0)
startTime  = time.time()
iterID     = 0

# Looping until time limit is reached
while 1:

    # First line for each iteration
    outputFile.write( 'Iteration ' + str(iterID).zfill(6) + '\n' )

    # Checking if time limit was reached.
    currentDuration =  float( time.time() - startTime )
    if currentDuration >= finalBreak:
        break

    # Generating some uncorrelated reandom variables
    X = np.random.random( ( numVars, 20000 ) )

    # Creating artificial correlation among them
    numCorrelatedVars = np.random.randint( 100, high=100000, size=1 )
    i1 = np.random.randint( 0, high=numVars-1, size=numCorrelatedVars )
    i2 = np.random.randint( 0, high=numVars-1, size=numCorrelatedVars )
    for j in range(numCorrelatedVars):
        X[i1[j],:] = ( X[i1[j],:] + X[i2[j],:] ) / 2.

    # Calculating their covariance matrix and evaluating
    # their eigenvalues and eigenvectors
    covMat = np.cov(X)
    w, v   = np.linalg.eig( covMat )

    # Writing the sorted eigenvalues
    outputFile.write( str( np.sort( np.abs(w) )[-1:-15:-1] ) )

    # Separation between iterations
    outputFile.write('\n---\n')

    # updating iteration variable
    iterID += 1

    ## To avoid an excessively large output file,
    ## let's limit it to the last 3000 lines every
    ## thousand iterations.
    if iterID > 1000:
        outputFile.close()
        os.system("tail -n 3000 output.dat > output.dat")
        outputFile = open('output.dat', 'w', 0)


print( 'The end, my friend' )
