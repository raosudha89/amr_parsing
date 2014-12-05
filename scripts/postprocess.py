import sys

argv = sys.argv[1:]
sentences_file = open(argv[0])
pos_file = open(argv[1])
new_pos_file = open(argv[2], 'w')

word_pos = []

for pos_line in pos_file.readlines():
	word_pos += pos_line.split()

for sentence in sentences_file.readlines():
	new_pos_line = ""
	words = sentence.split()
	for i in range(len(words)):
		if words[i] != word_pos[i].split("_")[0]:
			print words[i],  word_pos[i].split("_")[0]
			print "error!", sentence, word_pos[:len(words)]
			sys.exit()
		new_pos_line += word_pos[i] + " "
	word_pos = word_pos[len(words):]
	new_pos_file.write(new_pos_line + "\n")
