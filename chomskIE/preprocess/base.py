"""This script defines an abstract base :class: `Preprocesser`
with abstract methods :func: `fit` and :func: `transform,
which transform the input data based on each preprocessing
subclass' functionality.
"""


from abc import ABC, abstractmethod


class Preprocesser(ABC):
	"""An abstract class with :func: `fit` and :func: `transform`
	which preprocesses the given data based on it's functionality.
	"""
	@abstractmethod
	def _validate_input(self):
		"""An abstract method which needs to be declared in the
		subclasses. Checks whether the format of input matches
		that expected by the subclass' :fit: method.
		"""
		pass

	@abstractmethod
	def fit(self):
		"""An abstract method which needs to be declared in the
		subclasses. Transforms training data according to the
		functionality of the subclass.
		"""
		pass

	@abstractmethod
	def transform(self):
		"""An abstract method which needs to be declared in the
		subclasses. Transforms given sentence according to the
		functionality of the subclass.
		"""
		pass
