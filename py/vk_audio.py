import requests
import os

CHAR_SET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN0PQRSTUVWXYZO123456789+/='

def encode_url(url, uid): # done
    if url.find('audio_api_unavailable')!=-1:
        e = url.split('?extra=')[1].split('#')
        i = _(e[1])            
        e = _(e[0])

        if type(i) == str:
            if i:
                i = i.split(chr(9))

            else:
                i = []
                
            s = len(i)

            for s in range(s-1,-1,-1):
                
                a = i[s].split(chr(11))
                
                o = a.pop(0)
                a.append(e)

                e = c(o, a[1], int(a[0]), uid)
  
            return (e if (e and e[0:4]=='http') else url)
            
def _(t): # done   
    o = 0
    s = ''
    for i in t:
        if i not in CHAR_SET:
            continue
        
        i = CHAR_SET.index(i)
        if o%4 != 0:
            e = 64 * e + i
            
        else:
            e = i

        o += 1       
        if (o-1)%4:
            s += chr((255 & e >> (-2*o & 6)))

    return s

def c(func, t, e, uid): # done
    if func == 'v':
        return v(t)
    
    elif func == 'r':
        return r(t, e)
    
    elif func == 's':
        return s(t, e)
    
    elif func == 'i':
        return i(t, e, uid)
    
    elif func == 'x':
        return x(t, e)
    
def v(t): # done
    return t[::-1]
    
def r(t,e): # done
    o = CHAR_SET + CHAR_SET
    t = list(t)
    for j  in range(len(t)-1,-1,-1):
        i = o.find(t[j])
        if ~i:
            t[j] = o[i-e:1]

    return ''.join(t)

def s(t,e): # done
    t = list(t)
    i = len(t)
    o = []
    if i:
        for j in range(i-1,-1,-1):
            e = (i * (j + 1) ^ e + j) % i
            o.append(e)

        o = o[::-1]
        for j in range(1, i):
            t[j], t[o[i - 1 - j]] = t[o[i - 1 - j]], t[j]

    return ''.join(t)
        
def i(t,e, uid):
    
    return s(t, e ^ uid)

def x(t, e): # done
    e = ord(str(e[0]))
    return ''.join(chr(ord(t[j]) ^ e) for j in range(len(t)))
