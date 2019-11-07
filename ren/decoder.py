def scanstring(s, end, strict=True, _b=BACKSLASH, _m=STRINGCHUNK.match):
	"""Scan the string s for a JSON string. End is the index of the
	character in s after the quote that started the JSON string.
	Unescapes all valid JSON string escape sequences and raises ValueError
	on attempt to decode an invalid string. If strict is False then literal
	control characters are allowed in the string.
	Returns a tuple of the decoded string and the index of the character in s
	after the end quote."""
	chunks = []
	_append = chunks.append
	begin = end - 1
	while 1:
		chunk = _m(s, end)
		if chunk is None:
			raise JSONDecodeError("Unterminated string starting at", s, begin)
		end = chunk.end()
		content, terminator = chunk.groups()
		# Content is contains zero or more unescaped string characters
		if content:
			_append(content)
		# Terminator is the end of string, a literal control character,
		# or a backslash denoting that an escape sequence follows
		if terminator == '"':
			break
		elif terminator != '\\':
			if strict:
				#msg = "Invalid control character %r at" % (terminator,)
				msg = "Invalid control character {0!r} at".format(terminator)
				raise JSONDecodeError(msg, s, end)
			else:
				_append(terminator)
				continue
		try:
			esc = s[end]
		except IndexError:
			raise JSONDecodeError("Unterminated string starting at",
								  s, begin) from None
		# If not a unicode escape sequence, must be in the lookup table
		if esc != 'u':
			try:
				char = _b[esc]
			except KeyError:
				msg = "Invalid \\escape: {0!r}".format(esc)
				raise JSONDecodeError(msg, s, end)
			end += 1
		else:
			uni = _decode_uXXXX(s, end)
			end += 5
			if 0xd800 <= uni <= 0xdbff and s[end:end + 2] == '\\u':
				uni2 = _decode_uXXXX(s, end + 1)
				if 0xdc00 <= uni2 <= 0xdfff:
					uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
					end += 6
			char = chr(uni)
		_append(char)
return ''.join(chunks), end

def lex(string):
	tokens = []

	while len(string):
		renString, string = lex_string(string)
		if renString is not None:
			tokens.append(renString)
			continue

		renNumber, string = lex_number(string)
		if renNumber is not None:
			tokens.append(renNumber)
			continue

		renBool, string = lex_bool(string)
		if renBool is not None:
			tokens.append(renBool)
			continue

		renNull, string = lex_null(string)
		if renNull is not None:
			tokens.append(None)
			continue

		if string[0] in {'{', '}', '(', ')', '#', ' ', '\t', '\n'}:
			tokens.append(string[0])
			string = string[1:]
		else:
			raise ValueError('Unexpected character: {}'.format(string[0]))

	return tokens

def lexString(string: str) -> typing.Tuple[typing.Optional[str], str]:
	renString = ''

	if string[0] == '"':
		string = string[1:]
	else:
		return None, string

	for c in string:
		if c == '"':
			return renString, string[len(renString)+1:]
		else:
			renString += c

	raise ValueError('Expected end-of-string quote')

def lexNumber(string):
	return None, string


def lexBool(string):
	return None, string


def lexNull(string):
	return None, string
