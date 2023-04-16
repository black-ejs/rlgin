import DQN

if __name__ == '__main__':
    aa = [1,2,3,4,5,6,7,8]
    mx = DQN.argmax(aa)
    print(f"mx: {mx}  from {aa}")
    
    aa = [8,7,6,5,4,3,2,1]
    mx = DQN.argmax(aa)
    print(f"mx: {mx}  from {aa}")


    aa = [-8,-7,-6,-5,-4,-3,-2,-1]
    mx = DQN.argmax(aa)
    print(f"mx: {mx}  from {aa}")

    aa = [-5,-67,-16,5,4,-13,-294398,4]
    mx = DQN.argmax(aa)
    print(f"mx: {mx}  from {aa}")
