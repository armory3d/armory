
/* C API */

void trace(const char* s);
void tracef(float f);
void tracei(int i);

typedef void(*func_update)(void);
void notify_on_update(func_update f);
void remove_update(func_update f);

int get_object(const char* name);
void set_transform(int object, float x, float y, float z, float rx, float ry, float rz, float sx, float sy, float sz);
void set_location(int object, float x, float y, float z);
void set_scale(int object, float x, float y, float z);
void set_rotation(int object, float x, float y, float z);

int mouse_x(void);
int mouse_y(void);
int mouse_started(int button);
int mouse_down(int button);
int mouse_released(int button);
int key_started(int key); // kha.input.KeyCode
int key_down(int key);
int key_released(int key);

float time_real(void);
float time_delta(void);

void js_eval(const char* fn);
void js_call_object(int object, const char* fn);
void js_call_static(const char* path, const char* fn);

/* C template
#define WASM_EXPORT __attribute__((visibility("default")))

void logs(const char* s);

WASM_EXPORT
int main() {
  logs("Hello, world!");
  return 0;
}
*/
