import re
import argparse

from Crypto.Cipher import AES
from bitstring import Bits
from random import randint
from sys import byteorder

cycles = 0


def rounds(right, left, key, roundnum, decrypt):
    """
    Does the repetitions of the Feistel Network.
    The value of decrypt dictates whether the Feistel is reversed
    or not. Reversed Feistel is used for the decryption only.
    """
    """ print("\n-----------------")
    print("Right Key: " + right.bin)
    print("Left Key:  " + left.bin)
    print("-----------------\n")
    print("Starting AES Rounds..") """

    if decrypt:
        for r in range(roundnum-1, -1, -1):
            # In order to decrypt, we need to reverse the order of the
            # AES input blocks, hence we need to reverse roundnum order.
            # Round is 101 bits as to make the total block size 128-bits
            #print("Decrypting Round: " + repr(r+1))
            round = Bits(uint = r, length = 101)
            #print("-----------------")

            temp = left
            left = aes_enc(left, key, round) ^ right
            right = temp
            #print("Right Key: " + right.bin)
            #print("Left Key:  " + left.bin)
            #print("-----------------")
    else:
        for r in range(0, roundnum):
            # Round is 101 bits as to make the total block size 128-bits
            #print("Round Number: " + repr(r+1))
            round = Bits(uint = r, length = 101)
            #print("-----------------")

            temp = right
            right = aes_enc(right, key, round) ^ left
            left = temp
            #print("Right Key: " + right.bin)
            #print("Left Key:  " + left.bin)
            #print("-----------------")

    # In order to display the number properly we need to pad it to 64 bits.
    # Otherwise, we will get a negative, wrong value
    pad = Bits(bin="0000000000")
    whole = pad + left + right

    return whole.int


def aes_enc(half, key, round):
    """
    This is the AES encryption used for each round in the Feistel network.
    We use ECB with no problem since we encrypt only one block with it.
    """

    encrypter = AES.new(key.encode("utf8"), AES.MODE_ECB)
    block = half + round
    output = encrypter.encrypt(block.bin.encode("utf8"))

    # The output is in hex bytes format, if we iterate through it we can
    # get the decimal value of every digit
    output = ''.join([str(x) for x in output])
    output = bin(int(output))
    output = output[2:29]

    return Bits(bin = output)


def mainloop(cardnum, key, roundnum, decrypt):
    """
    This loop keeps the Feistel going until we get a 16 digit number.
    """

    global cycles
    # This regex is used to display the number in groups of four digits
    card = re.findall('\d{4}', repr(cardnum))
    #if cycles == 0:
        #print("Card Number: " + ' '.join(num for num in card))
    # Turn the card number into a binary number with exactly 54 digits
    cardnum = Bits(uint = cardnum, length = 54)

    # Split the number into two 27-bit numbers
    left = cardnum[:27]
    right = cardnum[27:]

    while True:
        result = rounds(right, left, key, roundnum, decrypt)

        if len(repr(result)) > 16:
            # We need exactly 16 digits. If we have more, we start again
            #print("\nThe result is more than 16 digits, cycling...")
            cycles += 1
            result = Bits(uint = result, length = 54)

            left = result[:27]
            right = result[27:]
        else:
            result = format(result, "016d")
            output = re.findall('\d{4}', repr(result))
            #print("Result: " + ' '.join(num for num in output) + "\n")
            #print("Cycled " + repr(cycles) + " times!")
            return result
