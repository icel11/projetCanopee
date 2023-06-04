from io import BytesIO

import scipy.misc
import tensorflow as tf


class Logger(object):

    def __init__(self, log_dir):
        #self.writer = tf.summary.FileWriter(log_dir)
        self.writer = tf.summary.create_file_writer(log_dir)

    def scalar_summary(self, tag, value, step):
        with self.writer.as_default():
            tf.summary.scalar(tag,value,step=step)
            self.writer.flush()

    def image_summary(self, tag, image, step):
        s = BytesIO()
        scipy.misc.toimage(image).save(s, format="png")

        # Create an Image object
        img_sum = tf.summary.image("picture", data=s.getvalue())

        # Create and write Summary
        with self.writer.as_default():
            summary = tf.summary.scalar(tag,data=img_sum,step=step)
            self.writer.add_summary(summary, step)
            self.writer.flush()

        self.writer.flush()

    def image_list_summary(self, tag, images, step):
        if len(images) == 0:
            return
        img_summaries = []
        for i, img in enumerate(images):
            s = BytesIO()
            scipy.misc.toimage(img).save(s, format="png")

            # Create an Image object
            img_sum = tf.summary.image("picture",data=s.getvalue())

            # Create a Summary value
            img_summaries.append(img_sum)

        # Create and write Summary
        with self.writer.as_default():
            summary = tf.summary.scalar(tag,data=img_summaries,step=step)
            self.writer.add_summary(summary, step)
            self.writer.flush()
