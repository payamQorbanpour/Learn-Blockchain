import hashlib, json, sys
import random


def hashMe(msg=""):
    #a helper that wraps hashing algorithm
    if type(msg) != str:
        msg = json.dumps(msg, sort_keys=True)

    if sys.version_info.major == 2:
        return unicode(hashlib.sha256(msg).hexdigest(), 'utf-8')
    else:
        return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()

def makeTransaction(maxValue=3):
    sign = int(random.getrandbits(1)) * 2 - 1
    amount = random.randint(1, maxValue)
    alicePays = sign * amount
    bobPays = -1 * alicePays
    return {u'Alice': alicePays, u'Bob': bobPays}

def make_buffer():
    txnBuffer = [makeTransaction() for i in range(2)]
    return txnBuffer

def updateState(txn, state):
    state = state.copy()
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state

def isValidTxn(txn, state):
    if sum(txn.values()) is not 0:
        return False

    for key in txn.keys():
        if key in state.keys():
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            return False
    return True

def init():
    state = {u'Alice': 50, u'Bob': 50}
    genesisBlockTxns = [state]
    genesisBlockContents = {u'blockNumber': 0, u'parentHash': None, u'txnCount':1, u'txns': genesisBlockTxns}
    genesisHash = hashMe(genesisBlockContents)
    genesisBlock = {u'hash': genesisHash, u'contents': genesisBlockContents}
    genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

    chain = [genesisBlock]
    return state, chain

def makeBlock(txns, chain):
    parentBlock = chain[-1]
    parentHash = parentBlock[u'hash']
    blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
    txnCount = len(txns)
    blockContents = {u'blockNumber': blockNumber, u'parentHash': parentHash, u'txnCount': len(txns), 'txns': txns}
    blockHash = hashMe(blockContents)
    block = {u'hash': blockHash, u'contents': blockContents}

    return block

def add_block(txnBuffer, state, chain, blockSizeLimit=2):
    while len(txnBuffer) > 0:
        bufferStartSize = len(txnBuffer)

        txnList = []
        while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
            newTxn = txnBuffer.pop()
            validTxn = isValidTxn(newTxn, state)

            if validTxn:
                txnList.append(newTxn)
                state = updateState(newTxn, state)
            else:
                print('ignored transaction')
                sys.stdout.flush()
                contuinue

        myBlock = makeBlock(txnList, chain)
        chain.append(myBlock)

def checkBlockHash(block):
    expectedHash = hashMe(block['contents'])
    if block['hash'] != expectedHash:
        raise Exception('Hash does not match contents of block {}'.format(block['contents']['blockNumber']))

    return

def checkBlockValidity(block, parent, state):
    parrentNumber = parent['contents']['blockNumber']
    parentHash = parent['hash']
    blockNumber = block['contents']['blockNumber']

    for txn in block['contents']['txns']:
        if isValidTxn(txn, state):
            state = updateState(txn, state)
        else:
            raise Exception('invalid transaction in block {}: {}'.format(blockNumber, txn))
    checkBlockHash(block)

    if blockNumber != (parrentNumber + 1):
        raise Exception('hash does not match contents of block {}'.format(blockNumber))

    if block['contents']['parentHash'] != parentHash:
        raise Exception('parent hash not accurate at block {}'.format(blockNumber))

    return state

def checkChain(chain):
    if type(chain) == str:
        try:
            chain = json.loads(chain)
            assert(type(chain) == list)
        except :
            return False
    elif type(chain) != list:
        return False

    state = {}

    for txn in chain[0]['contents']['txns']:
        state = updateState(txn, state)
    checkBlockHash(chain[0])
    parent = chain[0]

    for block in chain[1:]:
        state = checkBlockValidity(block, parent, state)
        parent = block

    return state

def show_chain(chain):
    print("\n\n----------------Current-Chain----------------\n")
    end='\n\n'
    sep=':\t'
    for i, block in enumerate(chain):
        print(i,block,sep,end)
    print("----------------End-of-Current-Chain----------------\n\n")

def main():
    state, chain = init()
    a = 'show the chain'
    b = 'make new transactions (random)'
    c = 'show new transactions'
    d = 'add new transactions to blockchain (do b first)'
    while(True):
        print("\n\n----------------Choose-Action----------------")
        action = input("Choose the action (enter the letter only):\n\ta:{}\n\tb: {}\n\tc: {}\n\td: {}\n".format(a,b,c,d))
        if action == "a":
            show_chain(chain)
        elif action == "b":
            bf = make_buffer()
        elif action == "c":
            print("new transactions:\n\t{}".format(bf))
        elif action == "d":
            add_block(bf, state, chain)

if __name__ == "__main__":
    main()
