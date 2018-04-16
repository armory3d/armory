
/* C API */

void trace(const char* s);
void tracef(float f);
void tracei(int i);
typedef void(*func_update)(void);
void notify_on_update(func_update f);
void remove_update(func_update f);
int get_object(const char* name);
void set_transform(int object, float x, float y, float z, float rx, float ry, float rz, float sx, float sy, float sz);

/* C template
#define WASM_EXPORT __attribute__((visibility("default")))

void logs(const char* s);

WASM_EXPORT int main() {
  logs("Hello, world!");
  return 0;
}
*/
