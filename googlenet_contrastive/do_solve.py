def do_solve(niter, solver, disp_interval, test_interval, test_iters, training_id, batch_size):
    """Run solvers for niter iterations,
       returning the loss and recorded each iteration.
       `solvers` is a list of (name, solver) tuples."""

    import tempfile
    import numpy as np
    import os
    from pylab import zeros, arange, subplots, plt, savefig
    import glob
    import time

    # SET PLOTS DATA
    # train_loss = zeros(niter/disp_interval)
    train_loss_r = zeros(niter/disp_interval)
    train_correct_pairs = zeros(niter/disp_interval)
    # train_acc = zeros(niter/disp_interval)


    # val_loss = zeros(niter/test_interval)
    val_loss_r = zeros(niter/test_interval)
    val_correct_pairs = zeros(niter/test_interval)
    # val_acc = zeros(niter/test_interval)


    it_axes = (arange(niter) * disp_interval) + disp_interval
    it_val_axes = (arange(niter) * test_interval) + test_interval

    _, ax1 = subplots()
    ax2 = ax1.twinx()
    ax1.set_xlabel('iteration')
    ax1.set_ylabel('train loss (r), val loss (g),')# train loss_r (c), val loss_r (o)')
    ax2.set_ylabel('train correct pairs (b) val correct pairs (m)')# train top1 (y) val top1 (bk)')
    ax2.set_autoscaley_on(False)
    ax2.set_ylim([0, batch_size])


    # loss = {name: np.zeros(niter) for name, _ in solvers}
    loss_r = np.zeros(niter)
    correct_pairs = np.zeros(niter)
    # acc = {name: np.zeros(niter) for name, _ in solvers}

    lowest_val_loss = 1000
    best_it = 0

    #RUN TRAINING
    for it in range(niter):
        # start = time.time()
        solver.step(1)  # run a single SGD step in Caffe
        # end = time.time()
        # print "Time step: " + str((end - start))
        # print "Max before ReLU: " + str(np.max(s.net.blobs['inception_5b/pool_proj'].data))
        # print "Max last FC: " + str(np.max(s.net.blobs['loss3/classifierCustom'].data))

        #loss[name][it] = s.net.blobs['loss3/loss3/classification'].data.copy()
        loss_r[it] = solver.net.blobs['loss3/loss3/ranking'].data.copy()
        correct_pairs[it] = solver.net.blobs['correct_pairs'].data.copy()
        # acc[name][it] = s.net.blobs['loss3/top-1'].data.copy()

        #PLOT
        if it % disp_interval == 0 or it + 1 == niter:
            # loss_disp = 'loss=' + str(loss['my_solver'][it]) + ' correct_pairs=' + str(correct_pairs['my_solver'][it]) + ' loss ranking=' + str(loss_r['my_solver'][it])
            loss_disp = ' correct_pairs=' + str(correct_pairs[it]) + ' loss ranking=' + str(loss_r[it])

            print '%3d) %s' % (it, loss_disp)

            # train_loss[it/disp_interval] = loss[it]
            train_loss_r[it/disp_interval] = loss_r[it]
            train_correct_pairs[it/disp_interval] = correct_pairs[it]
            # train_acc[it/disp_interval] = acc[it] *120


            # ax1.plot(it_axes[0:it/disp_interval], train_loss[0:it/disp_interval], 'r')
            ax1.plot(it_axes[0:it/disp_interval], train_loss_r[0:it/disp_interval], 'c')
            ax2.plot(it_axes[0:it/disp_interval], train_correct_pairs[0:it/disp_interval], 'b')
            # ax2.plot(it_axes[0:it/disp_interval], train_acc[0:it/disp_interval], 'gold')

            # if it > test_interval:
            #     ax1.plot(it_val_axes[0:it/test_interval], val_loss[0:it/test_interval], 'g') #Val always on top
            ax1.set_ylim([0,2])
            plt.title(training_id)
            plt.ion()
            plt.grid(True)
            plt.show()
            plt.pause(0.001)
            # title = '../training/numbers/training-' + str(it) + '.png'  # Save graph to disk
            # savefig(title, bbox_inches='tight')

        #VALIDATE
        if it % test_interval == 0 and it > 0:
            # loss_val = 0
            loss_val_r = 0
            cur_correct_pairs = 0
            # cur_acc = 0

            for i in range(test_iters):
                solver.test_nets[0].forward()
                # loss_val += solver.test_nets[0].blobs['loss3/loss3/classification'].data
                loss_val_r += solver.test_nets[0].blobs['loss3/loss3/ranking'].data
                cur_correct_pairs += solver.test_nets[0].blobs['correct_pairs'].data
                # cur_acc += solvers[0][1].test_nets[0].blobs['loss3/top-1'].data

            # loss_val /= test_iters
            loss_val_r /= test_iters
            cur_correct_pairs /= test_iters
            # cur_acc /= test_iters
            # cur_acc *= 120

            # print("Val loss: " + str(loss_val) + " Val correct pairs: " + str(cur_correct_pairs) + " Val loss ranking: " + str(loss_val_r) + "Val acc: "+ str(cur_acc))
            print(" Val correct pairs: " + str(cur_correct_pairs) + " Val loss ranking: " + str(loss_val_r))

            # val_loss[it/test_interval - 1] = loss_val
            val_loss_r[it/test_interval - 1] = loss_val_r
            val_correct_pairs[it/test_interval - 1] = cur_correct_pairs
            # val_acc[it/test_interval - 1] = cur_acc

            # ax1.plot(it_val_axes[0:it/test_interval], val_loss[0:it/test_interval], 'g')
            ax1.plot(it_val_axes[0:it/test_interval], val_loss_r[0:it/test_interval], 'orange')
            ax2.plot(it_val_axes[0:it/test_interval], val_correct_pairs[0:it/test_interval], 'm')
            # ax2.plot(it_val_axes[0:it/test_interval], val_acc[0:it/test_interval], 'k')
            ax1.set_ylim([0,2])
            ax1.set_xlabel('iteration ' + 'Best it: ' + str(best_it) + ' Best Val Loss: ' + str(int(lowest_val_loss)))
            plt.title(training_id)
            plt.ion()
            plt.grid(True)
            plt.show()
            plt.pause(0.001)
            title = '../../../hd/datasets/instaFashion/models/training/' + training_id + str(it) + '.png'  # Save graph to disk
            savefig(title, bbox_inches='tight')

            if loss_val_r < lowest_val_loss:
                print("Best Val loss!")
                lowest_val_loss = loss_val_r
                best_it = it
                filename = '../../../hd/datasets/instaFashion/models/CNNContrastive/' + training_id + 'best_valLoss_' + str(
                    int(loss_val_r)) + '_it_' + str(it) + '.caffemodel'
                prefix = 30
                for cur_filename in glob.glob(filename[:-prefix] + '*'):
                    print(cur_filename)
                    os.remove(cur_filename)
                solver.net.save(filename)
