import random
import string
from random import randint

class RandomSupport(object):
	"""Simple random data helpers.
	"""

	@classmethod
	def generate_number(cls):
		"""Generate a random number.

		Returns:
			int: the number
		"""
		return randint(0, 99999999999999)

	@classmethod
	def generate_number_between(cls, min, max):
		"""Generate a random number.

		Args:
			min (int): minimum for the generated value
			max (int): maximum for the generated value

		Returns:
			int: the number
		"""
		return randint(min, max)

	@classmethod
	def generate_name(cls):
		"""Generate a random name.

		Returns:
			str: the name
		"""
		return "name" + str(randint(0, 99999999999999))

	@classmethod
	def generate_email(cls, email_ihub=True):
		"""Generate a random email.

		Args:
			email_automation (bool): returns an randomized @zendesk chat-qa email address instead.

		Return :
			str: the email
		"""
		if email_ihub:
			return "ihub" + cls.generate_alphanumeric_lower(length=20) + "@ntu.edu.sg"
		return "email+" + str(randint(0, 99999999999999)) + "@test.com"

	@classmethod
	def generate_msg(cls):
		"""Generate a random message.

		Returns:
			str: the message
		"""
		return "msg_" + cls.generate_string()

	@classmethod
	def generate_string(cls, length=14):
		"""Generate a random string without numbers.

		Args:
			length (int): required length of the string

		Returns:
			str: (mostly)random string
		"""
		return ''.join(random.choice(string.ascii_uppercase
			+ string.ascii_lowercase)
			for _ in range(length))

	@classmethod
	def generate_numeric(cls, length=14):
		"""Generate a random numeric string.

		Args:
			length (int): required length of the string

		Returns:
			str: (mostly)random string
		"""
		return ''.join(random.choice(string.digits)
			for _ in range(length))

	@classmethod
	def generate_alphanumeric(cls, length=14):
		"""Generate a random string, upper and lowercase chars, numbers.

		Args:
			length (int): required length of the string

		Returns:
			str: (mostly)random string
		"""
		return ''.join(random.choice(string.ascii_uppercase
			+ string.ascii_lowercase
			+ string.digits)
			for _ in range(length))

	@classmethod
	def generate_alphanumeric_lower(cls, length=14):
		"""Generate a random string, lowercase chars, numbers.

		Args:
			length (int): required length of the string

		Returns:
			str: (mostly)random string
		"""
		return ''.join(random.choice(string.ascii_lowercase
			+ string.digits)
			for _ in range(length))

	@classmethod
	def generate_ipv4_address(cls):
		"""Generate a random ipv4_address

		Returns:
			str: a random ipv4_address
		"""
		return '.'.join(map(str, [randint(1, 256) for _ in range(4)]))