'''
Ver 1.0.4

updata:

garbled_circuit dfs to generate the gate map

Eval class dfs find the key

'''

from Crypto.Cipher import AES
import numpy as np
import random
import string

'''
Encryption part

'''
def encrypt(key, message):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag =  cipher.encrypt_and_digest(message)
    nonce = cipher.nonce
    encrypt_mes = [
       ciphertext, tag, nonce
    ]
    return encrypt_mes

def decrypt(key, encrypt_mes):
    ciphertext, tag, nonce = encrypt_mes 
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    return plaintext

def checkSum(key, encrypt_mes):
    ciphertext, tag, nonce = encrypt_mes 
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
        return True
    except ValueError:
        return False

'''
Gate generation part

a, b is input
c is output

w & x = d
'''


def garbled_circuit_generator(keyA, keyB, Output, gate_type):
    if gate_type == 'AND':
        return gate_generator(keyA, keyB, Output, 'AND', [0,0,0,1])
    elif gate_type == 'OR':
        return gate_generator(keyA, keyB, Output, 'OR', [0,1,1,1])
    elif gate_type == 'XOR':
        return gate_generator(keyA, keyB, Output, 'XOR',[0,1,1,0])
    elif gate_type == 'NAND':
        return gate_generator(keyA, keyB, Output, 'NAND',[1,1,1,0])
    elif gate_type == 'NOR':
        return gate_generator(keyA, keyB, Output, 'NOR',[1,0,0,0])


def gate_generator(a, b, c, gate_type, result):
    gate = ['','','','']
    check = []
    col = []
    '''
    check_1 = encrypt(x1, d0) //first encryption
    col_1 = encrypt(w0, check_1[0]) //sceond encryptopn
    check_1[0] = '' //empty the encryption message
    '''

    for i in range(2):
        for j in range(2):
            temp1 = encrypt(b[j], c[result[i * 2 + j]])
            temp2 = encrypt(a[i], temp1[0])
            col.append(temp2)
            temp1[0] = ' '
            check.append(temp1)

    indexOrder = np.random.permutation([0,1,2,3])

    gate[indexOrder[0]] = [col[0], check[0]]
    gate[indexOrder[1]] = [col[1], check[1]]
    gate[indexOrder[2]] = [col[2], check[2]]
    gate[indexOrder[3]] = [col[3], check[3]]
    
    gate_Info([[col[0], check[0]], [col[1], check[1]], [col[1], check[1]], [col[1], check[1]]],
    gate, result, indexOrder, gate_type
    )
    return gate

def gate_Info(prev_gate, after_gate,result, order, gate_type):

    gate_A = ['\'A','A']
    gate_B = ['\'B','B']
    gate_C = ['\'C','C']
    print('The ', gate_type)
    print('==============================================')
    for i in range(2):
        for j in range(2):
            print(result[i*2 + j],' Enc', gate_A[i] ,'\'(Enc', gate_B[j] ,'(', gate_C[result[i*2 + j]] ,')):', prev_gate[i*2 + j][0], '==>', order[i*2 + j], ':', after_gate[i*2 + j][0])
    print()


def key_repeat_check(key, key_list):
    if key in key_list:
        return True
    return False

def random_key(length):
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return bytes(result_str, 'ASCII')

def pair_key_generator(key_num, key_length):
    temp_key_list = [] #save generated key
    key_list = [] #formal the key
    for i in range(key_num*2) :
        tempKey = random_key(key_length)
        while(key_repeat_check(tempKey, temp_key_list)):
            tempKey = random_key(key_length)
        temp_key_list.append(tempKey)

    for i in range(key_num):
        key_list.append(
            [ temp_key_list[2 * i], temp_key_list[2 * i + 1] ]
            )

    return key_list

class node:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data

    def setChild(self, left_child, right_child):

        self.left = left_child
        self.right = right_child

    def getData(self):
        return self.data
#End of class Node
    
class Garbled_Circuit:
    #sample key = b'Sixteen byte key'

    def __init__(self, gateMap, gateNum, send_Message):
        #key setting
        
        key_length = 16

        self.travel = 0
        key_num = 1 + gateNum * 2

        self.inputKey = []

        self.key_list = pair_key_generator(key_num, key_length)
        send_Message[0] = bytes(send_Message[0], 'ASCII')
        send_Message[1] = bytes(send_Message[1], 'ASCII')
        self.key_list[0] = send_Message
        print(self.key_list)
        
        self.root = self.DFSGateMap(gateMap)


    def getRoot(self):
        myKey, myRoot = self.root
        return myRoot

    def getInputKey(self):
        key = []
        inKey = input('Please input your binary soluation :')
        print(self.inputKey)
        #int(inKey[0]) - 0  + 6
        #6 means first key index start in key_list[6]
        for i in range(len(self.inputKey)):
            key.append(self.inputKey[i][int(inKey[i])])
        
        #clear this table because Garbled_Circuit doesn't use this again
        self.key_list = []
        self.inputKey = []
        print('The input key generation : ')
        print()
        print('User input : ', inKey)
        print('Input key is : ', key)
        return key

    def DFSGateMap(self, gateMap):
        myKey = self.key_list[self.travel]
        self.travel = 1 + self.travel
        
        leftKey = None
        leftData = None
        rightKey = None
        rightData = None

        #leftSide gate
        if gateMap.left != None:
            leftKey, leftData = self.DFSGateMap(gateMap.left)
        else :
            leftKey = self.key_list[self.travel]
            self.travel = 1 + self.travel
            self.inputKey.append(leftKey)

        #rightSide gate
        if gateMap.right != None:
            rightKey, rightData = self.DFSGateMap(gateMap.right)
        else :
            rightKey = self.key_list[self.travel]
            self.travel = 1 + self.travel
            self.inputKey.append(rightKey)
        
        myGateData = garbled_circuit_generator(leftKey, rightKey, myKey, gateMap.data)
        myNode = node(myGateData)
        myNode.setChild(leftData, rightData)
        return [myKey, myNode]


#End of class function Garbled_Circuit

def find_key(keyA, keyB, gate):
    # 0 is col
    # 1 is check
    
    for i in range(4):
        colEncrypt = gate[i][0]
        check = gate[i][1]

        temp1 = decrypt(keyA, colEncrypt)
        check[0] = temp1
        temp2 = decrypt(keyB, check)
        if checkSum(keyB, check):
            return temp2

    print ("Error : Have Error in find_key function, It dosen't find any soluation")

#Eval class
class EvalGarbled:
    def __init__(self, gateMap, inputKey):
        self.travel = 0
        self.inputKey = inputKey
        self.msg = self.dfsEval(gateMap)

    def message(self):
        return self.msg

    def dfsEval(self, gateMap) :
        leftKey = None
        rightKey = None

        #print('DFS')
        if gateMap.left == None:
            leftKey = self.inputKey[self.travel]
            self.travel = self.travel + 1
        else:
            #print('Go left')
            leftKey = self.dfsEval(gateMap.left)

        if gateMap.right == None :
            rightKey = self.inputKey[self.travel]
            self.travel = self.travel + 1
        else:
            #print('Go right')
            rightKey = self.dfsEval(gateMap.right)

        #print(leftKey,' + ' ,rightKey)
        #print(gateMap.data)
        return find_key(leftKey, rightKey, gateMap.data)

#End of EvalGarbled 
if __name__ == "__main__":

    gateNum = 5

    AND1 = node('AND')
    XOR1 = node('XOR')
    OR1 = node('OR')
    NOR1 = node('NOR')
    NAND1 = node('NAND')

    XOR1.setChild(NAND1, NOR1)
    AND1.setChild(XOR1, OR1)
    gateMap = AND1

    GCMap = Garbled_Circuit(gateMap, gateNum, ['False', 'True'])
    intputKey = GCMap.getInputKey()
    GCMapRoot = GCMap.getRoot()

    Eval = EvalGarbled(GCMapRoot, intputKey)
    print(Eval.message())