def create_solver(train_net_path, test_net_path=None, base_lr=0.001):

    caffe_root = '../../caffe-master/'  # this file should be run from {caffe_root}/examples (otherwise change this line)
    import sys
    sys.path.insert(0, caffe_root + 'python')
    from caffe.proto import caffe_pb2

    s = caffe_pb2.SolverParameter()

    # Specify locations of the train and (maybe) test networks.
    s.train_net = train_net_path
    s.test_net.append(test_net_path)

    s.test_interval = 100000  # Test after every 1000 training iterations.
    s.test_iter.append(10)  # Test on 100 batches each time we test.

    # The number of iterations over which to average the gradient.
    # Effectively boosts the training batch size by the given factor, without
    # affecting memory utilization.
    s.iter_size = 1

    s.max_iter = 100000  # # of times to update the net (training iterations)

    # Solve using the stochastic gradient descent (SGD) algorithm.
    # Other choices include 'Adam' and 'RMSProp'.
    s.type = 'SGD'

    # Set the initial learning rate for SGD.
    s.base_lr = base_lr


    s.lr_policy = 'poly'
    s.power = 0.5

    # Set other SGD hyperparameters. Setting a non-zero `momentum` takes a
    # weighted average of the current gradient and previous gradients to make
    # learning more stable. L2 weight decay regularizes learning, to help prevent
    # the model from overfitting.
    s.momentum = 0.9
    s.weight_decay = 0.0002

    # Display the current training loss and accuracy every 1000 iterations.
    s.display = 1000000

    # Snapshots are files used to store networks we've trained.  Here, we'll
    # snapshot every 10K iterations -- ten times during training.
    s.snapshot = 1000
    s.snapshot_prefix = '../../../datasets/SocialMedia/models/CNNRegression/intagram_cities_GoogLeNet_'

    # Train on the GPU.  Using the CPU to train large networks is very slow.
    s.solver_mode = caffe_pb2.SolverParameter.GPU


    with open('solver.prototxt', 'w') as f:
        f.write(str(s))
        return f.name
