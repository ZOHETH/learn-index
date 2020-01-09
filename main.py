import pandas as pd
import time
import gc
from .b_tree import BTree
from .train_nn import TrainedNN

fliePath = "data/random.csv"
TOTAL_NUMBER=100
BLOCK_SIZE=100

def hybrid_training(stage_nums, core_nums, train_step, batch_size, data_x, data_y, threshold):
    stages_height = len(stage_nums)
    number_of_models = stage_nums[1]
    tmp_inputs = [[[] for i in range(number_of_models)] for i in range(stages_height)]
    tmp_labels = [[[] for i in range(number_of_models)] for i in range(stages_height)]
    index = [[None for i in range(number_of_models)] for i in range(stages_height)]
    tmp_inputs[0][0] = data_x
    tmp_labels[0][0] = []
    divisor=stage_nums[1]*1.0/(TOTAL_NUMBER/BLOCK_SIZE)
    # 对于为何一定要使用BLOCK_SIZE暂时不明确
    for k in data_y:
        tmp_labels[0][0].append(k*divisor)
        #这样labels的整数部分直接就是下一个stage中的序号
    for i in range(0, stages_height):
        for j in range(0, stage_nums[i]):
            inputs = tmp_inputs[i][j]
            labels = tmp_labels[i][j]
            tmp_index = TrainedNN(core_nums, train_step, batch_size, inputs, labels)
            tmp_index.train()

            index[i][j]=AbstractNN()  # 暂时不知道这个是干嘛的
            # 抽象训练出的结果，用于在下面输出预测和err

            del tmp_index
            gc.collect()
            # 处理内存 不知道是否需要

            if i < stages_height - 1:
                for ind in range(len(tmp_inputs[i][j])):
                    p = index[i][j].predict(tmp_inputs[i][j][ind])
                    # 得益于之前对tmp_label[0][0]的处理 这里得到的结果p直接就是下一层的序号
                    # 论文中的处理是 之前不做处理 在这里除以stages[i+1]
                    # 似乎并不一样 有待解决
                    if p > stage_nums[i + 1]:
                        p = stage_nums[i + 1]
                    tmp_inputs[i + 1][p].append(tmp_inputs[i][j][ind])
                    tmp_labels[i + 1][p].append(tmp_labels[i][j][ind])
                    # 每一个model里的input和label都是上一层直接传递下来的
    for i in range(stage_nums[stages_height - 1]):
        # 将最后一层替换为btree 这里还有很多疑问
        if index[stages_height - 1][i] is None:
            continue
        mean_abs_err = index[stages_height - 1][i].mean_err
        if mean_abs_err > threshold:
            print("Using BTree")
            index[stages_height - 1][i] = BTree(10)
            index[stages_height - 1][i].build(tmp_inputs[stages_height - 1][i], tmp_labels[stages_height - 1][i])
    return index


def train_index(path):
    data = pd.read_csv(path, header=None)
    train_x_set = []
    train_y_set = []
    stage_set = [1, 10]
    core_set = [[1, 1], [1, 1]]
    train_step_set = [20000, 20000]
    batch_size_set = [50, 50]
    threshold = 10

    global TOTAL_NUMBER
    TOTAL_NUMBER = data.shape[0]
    for i in range(data.shape[0]):
        train_x_set.append(data.iloc[i, 0])
        train_y_set.append(data.iloc[i, 1])
    # train_x_set=train_x_set[:] 不需要测试集！！ 不使用测试集可以得到准确的error
    # train_y_set=train_y_set[:]
    start_time = time.time()
    trained_index = hybrid_training(stage_set, core_set, train_step_set, batch_size_set,
                                    train_x_set, train_y_set, threshold)
    end_time = time.time()
    learn_time = end_time - start_time


def main():
