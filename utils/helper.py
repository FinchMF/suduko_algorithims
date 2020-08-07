

##########################################################
# H E L P E R  F U N C T I O N S for D C N N S O L V E R #
##########################################################


import copy
import keras
import numpy as np


def norm(a):
    return (a/9)-.5


def denorm(a):  
    return (a+.5)*9


def inference_sudoku(sample, model):
    
    '''
        This function solve the sudoku by filling blank positions one by one.
    '''
    
    feat = copy.copy(sample)
    
    while(1):
    
        out = model.predict(feat.reshape((1,9,9,1)))  
        out = out.squeeze()

        pred = np.argmax(out, axis=1).reshape((9,9))+1 
        prob = np.around(np.max(out, axis=1).reshape((9,9)), 2) 
        
        feat = denorm(feat).reshape((9,9))
        mask = (feat==0)
     
        if(mask.sum()==0):
            break
            
        prob_new = prob*mask
    
        ind = np.argmax(prob_new)
        x, y = (ind//9), (ind%9)

        val = pred[x][y]
        feat[x][y] = val
        feat = norm(feat)
    
    return pred


def test_accuracy(feats, labels, model):
    
    correct = 0
    
    for i,feat in enumerate(feats):
        
        pred = inference_sudoku(feat, model)
        
        true = labels[i].reshape((9,9))+1
        
        if(abs(true - pred).sum()==0):
            correct += 1
        
    print(correct/feats.shape[0])


def solve_sudoku(game, model):
    
    game = game.replace('\n', '')
    game = game.replace(' ', '')
    game = np.array([int(j) for j in game]).reshape((9,9,1))
    game = norm(game)
    game = inference_sudoku(game, model)
    return game