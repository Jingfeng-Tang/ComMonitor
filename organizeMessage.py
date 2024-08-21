def isHex(ch):
    if ch>='0'and ch<='9'or ch>='a'and ch<='z'or ch>='A'and ch<='Z'or ch == ' ':
        return True
    else :
        return False

def hexIsLegal(message):
    # 十六进制数据 检查是否非法0~F
    for i in range(len(message)):
        if isHex(message[i]) == False:
            return False
    return True

def organizeMsg(message):
    # 先按空格分开
    list_message = message.split(" ")
    org_message = ''
    for single_msg in list_message:
        if len(single_msg) % 2 != 0:
            single_msg1 = list(single_msg)
            single_msg1.insert(len(single_msg) - 1, '0')
            single_msg = ''.join(single_msg1)
        org_message = org_message + single_msg
        finalmsg = bytes.fromhex(org_message)
    #将str转换成对应的hex信息
    return finalmsg,org_message