import tensorflow as tf 

a = tf.constant([ [[1,2],[3,10] ],[ [1,2],[5,4] ]])
b = tf.constant([ [[2,1], [7,1]],[ [2,1], [3,9]]] )
# c = tf.constant([ [2,3], [4,5]])

def get_shape(tensor):
  static_shape = tensor.shape.as_list()
  dynamic_shape = tf.unstack(tf.shape(tensor))
  dims = [s[1] if s[0] is None else s[0]
          for s in zip(static_shape, dynamic_shape)]
  return dims

 
maxValue = tf.reduce_max(a + b,axis = -1,keep_dims=True)

choose = a + b
# result = tf.where(choose,tf.zeros_like(choose)) + tf.where(tf.equal(y,0),choose,tf.zeros_like(choose))
y = choose.get_shape().as_list()

z = tf.zeros_like(choose) 

with tf.Session() as sess:
    print( (a + b).eval())
    print(maxValue.eval())
    print(y)
    print(z) 

 

import tensorflow as tf

def add_and_keep_larger_elements(vector1, vector2):
    # 将两个向量相加
    result = tf.add(vector1, vector2)
    
    # 仅保留较大的元素
    result = tf.maximum(vector1, vector2)
    
    return result

# 示例用法
vector1 = tf.constant([1, 2, 3])
vector2 = tf.constant([4, 5, 6])
result = add_and_keep_larger_elements(a, b)

# 打印结果
with tf.Session() as sess:
    print(result.eval())
