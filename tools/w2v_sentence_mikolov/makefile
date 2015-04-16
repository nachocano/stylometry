CC = clang
#The -Ofast might not work with older versions of gcc; in that case, use -O2
CFLAGS = -lm -pthread -O2 -march=native -Wall -funroll-loops -Wunused-result

all: word2vec

word2vec : word2vec.c
	$(CC) word2vec.c -o word2vec $(CFLAGS)
	chmod +x *.sh

clean:
	rm -rf word2vec
