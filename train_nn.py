import tensorflow as tf
import numpy as np


class TrainedNN:
    def __init__(self, cores, train_step, train_x, train_y, learning_rate):
        self.core_nums = cores
        self.train_step_nums = train_step
        self.train_x = train_x
        self.train_y = train_y
        self.learning_rate=learning_rate
        self.sess = tf.Session()
        self.h_fc = []
        self.h_fc_drop = []
        self.w_fc = []
        self.b_fc = []
        self.cross_entropy=[]
        self.train_step

    def train(self):
        for i in range(len(self.core_nums) - 1):
            self.h_fc[i] = tf.nn.relu(tf.matmul(self.h_fc_drop[i], self.w_fc[i]) + self.b_fc[i])
            # 向量运算 初始的w和b 先进行向前传播
            # self.h_fc_drop[i+1]=tf.nn.dropout()
            # 防止过拟合，暂时先不用
        self.cross_entropy=tf.reduce_mean(tf.losses.mean_squared_error(self.y_,self.h_fc[len(self.core_nums)-2]))
        # 最后为什么是len(core_nums)-2
        # 因为对于一个n层的网络,
        # 需要推进n-1次,
        # n-1次后的结果是h[n-2](下标从零开始)
        self.train_step=tf.train.AdamOptimizer(self.learning_rate).minimize(self.cross_entropy)
        self.sess.run(tf.global_variables_initializer())

        for step in range(self.train_step_nums):
            self.sess.run(self.train_step,)

            if step%100==0:
                err=self.sess.run(self.cross_entropy,)
                print("cross_entropy: %f" % err)
                if step == 0:
                    last_err = err
                    # use threhold to stop train
                if self.useThreshold:
                    if err < self.threshold_nums:
                        return
                # not use threshold, stop when error stop decreasing
                elif err > last_err:
                    err_count += 1
                    if err_count == 10:
                        return
                last_err = err

            self.next_batch()
