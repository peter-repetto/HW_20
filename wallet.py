#Imports for Project
import subprocess
import json
import os
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from bit import wif_to_key, PrivateKeyTestnet
from bit.network import NetworkAPI
from eth_account import Account

#Generating The Mnemonic
mnemonic = os.getenv('MNEMONIC')
print(len(mnemonic))

# Create Coins
class coin:
    BTC = 'btc'
    ETH = 'eth'
    BTCTEST = 'btc-test'
    
#Deriving the wallet keys
def derive_wallets (mnemonic,coin,number):
    #Calling the wallet
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php --cols=address,index,path,privkey,pubkey,pubkeyhash,xprv,xpub --mnemonic="{mnemonic}" -g --numderive="{number}" --coin="{coin}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    #Reading Output or Error
    (output, err) =p.communicate()
    #This will allow you to wait as it closes the childprocess 
    p_status = p.wait()
    #Setting your keys
    keys = json.loads(output)
    return keys

# Output Ether
derive_wallets(mnemonic,ETH,3)

#Output Bitcoin
derive_wallets(mnemonic, BTC, 3)

#Output BTC Testnet
derive_wallets(mnemonic, BTCTEST,3)

# Defining the private key for the account
def priv_key_to_account (coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    else:
        return PrivateKeyTestnet(priv_key)
    
#Loading W3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

#Defining Keys 
key = {'eth':derive_wallets(ETH,mnemonic,3),'btc-test': derive_wallets(BTCTEST,mnemonic,3)}

#Accessing the ETH and BTC Accounts with the Private Keys  
eth_key = key['eth'][0]['privkey']
btc_key = key['btc-test'][0]['privkey']

#Accessing the ETH and BTC Accounts 
eth_account = priv_key_to_account(ETH, eth_privkey)
btc_account = priv_key_to_account(BTCTEST, btc_privkey)

#Defining Create Tokens 
def create_tx(coin, account, to, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
        {"from": eth_account.address, "to": to, "value": amount}
    )
        return {
            "from": eth_account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            
    }
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(btc_account.address, [(to, amount, BTC)])
    
#Defining Send Tokens 
def send_tx(coin,account, recipient, amount):
    tkns = create_tx(coin,account,recipient,amount)
    
    if coin == ETH:
        signed_tkns = eth_account.sign_transaction(tkns)
        result = w3.eth.sendRawTransaction(signed_tkns.rawTransaction)
        return result.hex()
    elif coin == BTCTEST:
        signed_tkns = btc_account.sign_transaction(tkns)
        return NetworkAPI.broadcast_tx_testnet(signed_tkns)
    
#Create ETH Tokens 
create_tx('ETH',eth_account,'0x722e8728D4eC8727Cad86bdA19241E3A1Dc85263',10)

#Sending ETH Tokens 
send_tx('ETH',eth_account,'0x722e8728D4eC8727Cad86bdA19241E3A1Dc85263', 10)

#Sending BTCTest Tokens 
send_tx(BTCTEST,btc_account,'n3sLNvyxBmCgddERiGDkedbhS55cow3n3T',.0001)



