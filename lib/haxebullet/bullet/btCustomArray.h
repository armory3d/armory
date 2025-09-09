#include <stdlib.h>

class btFloatArray {

	int count = 0;

	public:

		float *raw;

		btFloatArray(int num) {

			raw = (float *) malloc(sizeof(float) * num);
			count = num;
		}

		~btFloatArray() {

			free(raw);
		}

		float at(int pos) {

			return raw[pos];
		}

		int set(int pos, float value) {

			if(pos < count){
				raw[pos] = value;
				return 0;
			}

			return 1;
		}

		int size() {
			return count;
		}
};

class btIntArray {

	int count = 0;

	public:

		int *raw;

		btIntArray(int num) {

			raw = (int *) malloc(sizeof(int) * num);
			count = num;
		}

		~btIntArray() {

			free(raw);
		}

		float at(int pos) {

			return raw[pos];
		}

		int set(int pos, int value) {

			if(pos < count){
				raw[pos] = value;
				return 0;
			}

			return 1;
		}

		int size() {
			return count;
		}
};