from typing import List, Type, Tuple
import Functions
import Neuron
from BackPropMatrices import BackPropMatrices
from TrainingSet import TrainingSet
from NetworkTester import NetworkTester
from MatrixMath import MatrixMath
import numpy as np
import time


class NeuralNetwork:
    def __init__(self, layers_amount: int, neurons_amount: List[int], weight_matrix: List[List[float]],
                 act_functions: List[Type[Functions.FuncAbstract]], loss_function: Type[Functions.LossFuncAbstract]):
        # \/ \/Checking if parameters are legal.\/ \/
        assert layers_amount > 0, "layers_amount(%d) is not greater than 0" % layers_amount
        assert len(neurons_amount) == layers_amount,\
            "Size of neurons_amount list(%d) doesn't equal layers_amount(%d):\nneurons_amount: %s"\
            % (len(neurons_amount), layers_amount, neurons_amount)
        assert len(weight_matrix) == layers_amount,\
            "Size of weight_matrix list(%d) doesn't equal layer_amount(%d):\nweight_matrix: %s"\
            % (len(weight_matrix), layers_amount, weight_matrix)
        assert len(act_functions) == layers_amount,\
            "Size of act_functions list(%d) doesn't equal layers_amount(%d):\nact_functions: %s"\
            % (len(act_functions), layers_amount, act_functions)
        for k in range(1, layers_amount):
            assert neurons_amount[k-1] == len(weight_matrix[k])-1,\
                "Size of layer's (%d) output is (%d), but layer (%d) expects input of size (%d+1):" \
                "\nneurons_amount[%d]: %d\nlen(weight_matrix[%d]): %d" %\
                (k-1, neurons_amount[k-1], k, len(weight_matrix[k])-1,
                 k-1, neurons_amount[k-1], k, len(weight_matrix[k]))
        # /\ /\Checking if parameters are legal./\ /\
        # Initializing variables.
        self.loss_function = loss_function
        self.layers: List[List[Neuron.Neuron]] = []
        for layerK in range(layers_amount):
            self.layers.append([])
            for neuronN in range(neurons_amount[layerK]):
                self.layers[layerK].append(Neuron.Neuron(weight_matrix[layerK], act_functions[layerK]))
        #for k in range(layers_amount):  # TODO do wywalenia
            #print("LAYER %d" % k)
            #for n in range(neurons_amount[k]):
                #print(self.layers[k][n].activationFunction)
                #print(self.layers[k][n].weights)

    # \/\/ TRAINING STUFF \/\/
    def adjust_weights(self, adjust_matrix: List[List[List[float]]]):
        # Checking if adjust_matrix is legal.
        # TODO it's something wrong with this check for sure
        assert len(adjust_matrix) == len(self.layers)
        for k in range(len(self.layers)):
            for i in range(len(self.layers[k])):
                assert len(adjust_matrix[k][i]) == len(self.layers[k][i].weights)
        # Adjusting weights.
        for layerK in range(len(self.layers)):
            for neuronI in range(len(self.layers[layerK])):
                self.layers[layerK][neuronI].adjust_weights(adjust_matrix[layerK][neuronI])

    def examine_single_pair(self, input_data: List[float], answer: List[float]) -> List[List[List[float]]]:
        """Proceeds one training example and returns matrix of loss functions derivatives
        in respect to all weights - dq/dwkij"""
        back_prop_matrices = BackPropMatrices(self)

        # process result and save derivatives of activation function and layers' outputs
        result: List[float] = input_data.copy()
        for layerK in range(len(self.layers)):
            result.append(1)
            back_prop_matrices.y.append(result.copy())
            iteration_result: List[float] = []
            for neuronI in range(len(self.layers[layerK])):
                neuron_output: float = self.layers[layerK][neuronI].process_input(result)
                iteration_result.append(neuron_output)
                # TODO \/\/ probably can put this directly into matrix
                back_prop_matrices.set_deriv(layerK, neuronI,
                                             self.layers[layerK][neuronI].activationFunction.derivative(neuron_output))
            result = iteration_result
        back_prop_matrices.y.append(result.copy())
        #print("Input %s gave result: %s" % (input_data, result))
        #print("back_prop_matrices.y: %s" % back_prop_matrices.y)
        back_prop_matrices.init_last_dq_dykj(result.copy(), answer.copy())

        # calculating weights' derivatives matrix
        weight_derivs_matrix: List[List[List[float]]] = []  # dq/dwkij
        for layerK in range(len(self.layers)-1, -1, -1):
            layers_derivs_vectors: List[List[float]] = []
            for neuronI in range(len(self.layers[layerK])):
                derivs_vector: List[float] = []
                for weightJ in range(len(self.layers[layerK][neuronI].weights)):
                    #print("LAYER: %d ; NEURON: %d ; WEIGHT: %d" % (layerK, neuronI, weightJ))
                    dqdw: float = back_prop_matrices.afunc_derivs_matrix[layerK][neuronI] *\
                                  back_prop_matrices.y[layerK][weightJ]
                    dqdw = dqdw * back_prop_matrices.get_dq_dykj(layerK, neuronI)
                    derivs_vector.append(dqdw)
                layers_derivs_vectors.append(derivs_vector)
            weight_derivs_matrix = [layers_derivs_vectors] + weight_derivs_matrix  # prepend instead of append
        #print("WEIGHT %s" % weight_derivs_matrix)
        return weight_derivs_matrix

    def calc_gradientj(self, training_set: TrainingSet) -> List[List[List[float]]]:
        # gradient of J(w) function that we want to minimize
        gradient: List[List[List[float]]] = self.examine_single_pair(training_set.data[0], training_set.answers[0])
        #print("GRADIENT: %s" % gradient)
        for pairP in range(1, len(training_set.data), 1):
            #print("GRADIENT: %s" % gradient)
            #time.sleep(1)
            gradient = MatrixMath.add3d(gradient, self.examine_single_pair(training_set.data[pairP], training_set.answers[pairP]))
            #gradient = np.add(gradient, self.examine_single_pair(training_set.data[pairP], training_set.answers[pairP]))
        #print("GRADIENT %s" % gradient)
        scalar: float = 1 / len(training_set.data)
        #time.sleep(1)
        #print("GRADIENT 1 %s" % gradient)
        # multiply matrix by scalar cause numpy has no such function :)
        gradient = MatrixMath.mul_scalar3d(gradient, scalar)
        #print("GRADIENT 2 %s" % gradient)
        return gradient

    def train(self, training_set: TrainingSet, learning_rate: float, learning_target: float):
        assert 0 <= learning_target
        network_tester: NetworkTester = NetworkTester(self)
        test_result: Tuple[float, float] = network_tester.test(training_set)
        start_loss = test_result[0]
        print("###STARTING TRAINING...###\nBefore training:\nTarget function: %s\nCorrect ratio: %s\n" %
              (test_result[0], test_result[1]))

        iteration: int = 0
        while test_result[0] > learning_target and iteration < 1000:
            gradient: List[List[List[float]]] = self.calc_gradientj(training_set)
            #print(gradient)
            minus_beta_gradient = gradient.copy()
            #print(minus_beta_gradient)
            # multiply matrix by scalar
            minus_beta_gradient = MatrixMath.mul_scalar3d(minus_beta_gradient, -learning_rate)

            #print("ITERATION %d minus_beta_gradient: %s" % (iteration, minus_beta_gradient))
            #time.sleep(1)
            self.adjust_weights(minus_beta_gradient)
            new_result = network_tester.test(training_set)
            if new_result[0] > test_result[0]:
                print("#####Too big learning rate!#####")
            test_result = new_result
            iteration = iteration + 1
            print("\nAfter { %d } iterations:\nTarget function: %s\n"
                  % (iteration, test_result[0]))
        print("###END OF TRAINING###")
        print("\nTrained from loss function %s to %s\n" % (start_loss, test_result[0]))

    def kfold_train(self):  # TODO
        pass
    # /\/\ TRAINING STUFF /\/\

    def make_guess(self, input_vector: List[float]) -> List[float]:
        # Checking if input is legal.
        assert len(input_vector) == len(self.layers[0][0].weights)-1,\
            "Size of input_vector is (%d), but layer (0) expects input of size (%d+1):" \
            "\ninput_vector: %s\nself.layers[0][0].weights: %s" %\
            (len(input_vector), len(self.layers[0][0].weights)-1, input_vector, self.layers[0][0].weights)

        # Start of processing.
        result: List[float] = input_vector.copy()
        for layerK in range(len(self.layers)):
            result.append(1)
            iteration_result: List[float] = []
            for neuronI in range(len(self.layers[layerK])):
                iteration_result.append(self.layers[layerK][neuronI].process_input(result))
            result = iteration_result
        #print("Input %s gave result: %s" % (input_vector, result))
        return result
