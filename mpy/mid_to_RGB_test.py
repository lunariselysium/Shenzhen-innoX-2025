# -*- coding: utf-8 -*-
# 导入mido库,关于Python读取midi的文件有很多第三方的库
# 这里我们使用的是mido这个库.
import mido
#pip install mido -i https://pypi.tuna.tsinghua.edu.cn/simple
'''
输出每个midi文件中的每个动作
'''
def send_msg(file_name):
    # 返回midi对象
    # 这里调用了mido的库里MidiFile()方法.
    # 并把文件名"DY_kanong.mid"传了进去.
    # 这里返回的mid就包含了所读取 "DY_kanong.mid" 的所有信息,
    # mid这个名字是我们自己起的,然后他就包含了midi文件的信息,以后操作它就行了.
    # 其实实现方法大概是用到了类的思想,以后mid这个变量就是类了,他有很多操作函数.通过点来调用.
    mid=mido.MidiFile(file_name)
    # 下面是一个循环,然后就是操作mid这个变量,调用tracks方法,
    # 这里tracks代表了音轨的东西,每条音轨通常情况下就是一个乐器.
    for i, track in enumerate(mid.tracks):             # 用于遍历,组合成索引序列.
        #print('Track {}: {}'.format(i, track.name))    # 输出:Track 0: Piano 1
        # 上面一个循环是输出各条音轨,一个midi文件可以是好几条音轨合成的.每条音轨有一个乐器或多个乐器.
        # 下面这个循环是循环某一条音轨中的数据,输出音轨中的数据.
        # 音轨中记录的一系列钢琴按键按下和弹起的操作.
        for msg in track:
            msg = str(msg).split(' ')
            #print( msg)
            # 输出每个动作.
            if msg[0] == 'note_off' or msg[0] == 'note_on ':
                if msg[0] == 'note_on':
                    print([True,int(msg[2].split('=')[1]),int(msg[3].split('=')[1]),int(msg[4].split('=')[1])])
                else:
                    print([False,int(msg[2].split('=')[1]),int(msg[3].split('=')[1]),int(msg[4].split('=')[1])])

# 代表主函数
if __name__ == '__main__':
    # 调用函数
    send_msg('ode_of_joy.mid')