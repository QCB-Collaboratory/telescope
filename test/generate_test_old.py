import numpy as np
import time

finalBreak = 8*60*60
numVars    = 500
outputFile = open('output.dat', 'w', 0)

startTime = time.time()

iterID = 0

while 1:

    outputFile.write( 'Iteration ' + str(iterID).zfill(6) + '\n' )

    currentDuration =  float( time.time() - startTime )
    if currentDuration >= finalBreak:
        break

    X = np.random.random( ( numVars, 20000 ) )

    numCorrelatedVars = np.random.randint( 100, high=100000, size=1 )
    i1 = np.random.randint( 0, high=numVars-1, size=numCorrelatedVars )
    i2 = np.random.randint( 0, high=numVars-1, size=numCorrelatedVars )
    for j in range(numCorrelatedVars):
        X[i1[j],:] = ( X[i1[j],:] + X[i2[j],:] ) / 2.

    covMat = np.cov(X)
    w, v   = np.linalg.eig( covMat )

    outputFile.write( str( np.sort( np.abs(w) )[-1:-15:-1] ) )

    outputFile.write('\n---\n')

    iterID += 1

    if iterID > 1000:
        outputFile.close()
        os.system('tail -n 3000 output.dat > output.dat')
        outputFile = open('output.dat', 'w', 0)


print( 'The end, my friend' )
