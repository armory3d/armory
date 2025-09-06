#include <map>
#include <string>
#include <vector>
#include <kinc/log.h>
#include <kinc/io/filereader.h>
#include <kinc/io/filewriter.h>
#ifdef WITH_AUDIO
#include <kinc/audio1/audio.h>
#include <kinc/audio1/sound.h>
#include <kinc/audio2/audio.h>
#endif
#include <kinc/system.h>
#include <kinc/window.h>
#include <kinc/display.h>
#include <kinc/input/mouse.h>
#include <kinc/input/surface.h>
#include <kinc/input/keyboard.h>
#include <kinc/input/pen.h>
#include <kinc/input/gamepad.h>
#include <kinc/math/random.h>
#include <kinc/math/core.h>
#include <kinc/threads/thread.h>
#include <kinc/threads/mutex.h>
#include <kinc/network/http.h>
#include <kinc/graphics4/shader.h>
#include <kinc/graphics4/vertexbuffer.h>
#include <kinc/graphics4/indexbuffer.h>
#include <kinc/graphics4/graphics.h>
#include <kinc/graphics4/pipeline.h>
#include <kinc/graphics4/rendertarget.h>
#include <kinc/graphics4/texture.h>
#ifdef WITH_COMPUTE
#include <kinc/compute/compute.h>
#endif
#include <kinc/io/lz4/lz4.h>
#define STB_IMAGE_IMPLEMENTATION
#include <kinc/libs/stb_image.h>
#ifdef KORE_DIRECT3D11
#include <d3d11.h>
#endif

#include <libplatform/libplatform.h>
#ifdef KORE_LINUX // xlib defines conflicting with v8
#undef True
#undef False
#undef None
#undef Status
#endif
#include <v8.h>
#include <v8-fast-api-calls.h>

#ifdef KORE_WINDOWS
#include <Windows.h> // AttachConsole
#include <dwmapi.h>
#ifndef DWMWA_USE_IMMERSIVE_DARK_MODE
#define DWMWA_USE_IMMERSIVE_DARK_MODE 20
#endif
extern "C" struct HWND__ *kinc_windows_window_handle(int window_index); // Kore/Windows.h
bool show_window = false;
// Enable visual styles for ui controls
#pragma comment(linker,"\"/manifestdependency:type='win32' name='Microsoft.Windows.Common-Controls' version='6.0.0.0' processorArchitecture='*' publicKeyToken='6595b64144ccf1df' language='*'\"")
#endif

#ifdef WITH_WORKER
#include "worker.h"
#endif

using namespace v8;

#ifdef KORE_MACOS
extern "C" const char *macgetresourcepath();
#endif

namespace {
	int _argc;
	char **_argv;
	bool enable_window = true;
	#ifdef WITH_AUDIO
	bool enable_audio = true;
	#endif
	bool snapshot = false;
	bool stderr_created = false;
	bool in_background = false;
	int paused_frames = 0;

	Isolate *isolate;
	std::unique_ptr<Platform> plat;
	Global<Context> global_context;
	Global<Function> update_func;
	Global<Function> drop_files_func;
	Global<Function> cut_func;
	Global<Function> copy_func;
	Global<Function> paste_func;
	Global<Function> foreground_func;
	Global<Function> resume_func;
	Global<Function> pause_func;
	Global<Function> background_func;
	Global<Function> shutdown_func;
	Global<Function> keyboard_down_func;
	Global<Function> keyboard_up_func;
	Global<Function> keyboard_press_func;
	Global<Function> mouse_down_func;
	Global<Function> mouse_up_func;
	Global<Function> mouse_move_func;
	Global<Function> touch_down_func;
	Global<Function> touch_up_func;
	Global<Function> touch_move_func;
	Global<Function> mouse_wheel_func;
	Global<Function> pen_down_func;
	Global<Function> pen_up_func;
	Global<Function> pen_move_func;
	Global<Function> gamepad_axis_func;
	Global<Function> gamepad_button_func;
	Global<Function> save_and_quit_func;

	#ifdef WITH_AUDIO
	Global<Function> audio_func;
	kinc_mutex_t mutex;
	kinc_a2_buffer_t audio_buffer;
	int audio_read_location = 0;
	void update_audio(kinc_a2_buffer_t *buffer, int samples);
	#endif

	bool save_and_quit_func_set = false;
	void update(void *data);
	void drop_files(wchar_t *file_path, void *data);
	char *cut(void *data);
	char *copy(void *data);
	void paste(char *text, void *data);
	void foreground(void *data);
	void resume(void *data);
	void pause(void *data);
	void background(void *data);
	void shutdown(void *data);
	void key_down(int code, void *data);
	void key_up(int code, void *data);
	void key_press(unsigned int character, void *data);
	void mouse_move(int window, int x, int y, int mx, int my, void *data);
	void mouse_down(int window, int button, int x, int y, void *data);
	void mouse_up(int window, int button, int x, int y, void *data);
	void mouse_wheel(int window, int delta, void *data);
	void touch_move(int index, int x, int y);
	void touch_down(int index, int x, int y);
	void touch_up(int index, int x, int y);
	void pen_down(int window, int x, int y, float pressure);
	void pen_up(int window, int x, int y, float pressure);
	void pen_move(int window, int x, int y, float pressure);
	void gamepad_axis(int gamepad, int axis, float value);
	void gamepad_button(int gamepad, int button, float value);

	char temp_string[4096];
	char temp_string_vs[1024 * 1024];
	char temp_string_fs[1024 * 1024];
	char temp_string_vstruct[4][32][32];
	std::string assetsdir;
	#ifdef KORE_WINDOWS
	wchar_t temp_wstring[1024];
	wchar_t temp_wstring1[1024];
	#endif

	class KromCallbackdata {
	public:
		int32_t size;
		Global<Function> func;
	};

	void write_stack_trace(const char *stack_trace) {
		kinc_log(KINC_LOG_LEVEL_INFO, "Trace: %s", stack_trace);

		#ifdef KORE_WINDOWS
		FILE *file = fopen("stderr.txt", stderr_created ? "a" : "w");
		if (file == nullptr) { // Running from protected path
			strcpy(temp_string, kinc_internal_save_path());
			strcat(temp_string, "\\stderr.txt");
			file = fopen(temp_string, stderr_created ? "a" : "w");
		}
		if (file != nullptr) {
			stderr_created = true;
			fwrite(stack_trace, 1, strlen(stack_trace), file);
			fwrite("\n", 1, 1, file);
			fclose(file);
		}
		#endif
	}

	void handle_exception(TryCatch *try_catch) {
		MaybeLocal<Value> trace = try_catch->StackTrace(isolate->GetCurrentContext());
		if (trace.IsEmpty()) {
			String::Utf8Value stack_trace(isolate, try_catch->Message()->Get());
			write_stack_trace(*stack_trace);
		}
		else {
			String::Utf8Value stack_trace(isolate, trace.ToLocalChecked());
			write_stack_trace(*stack_trace);
		}
	}

	void krom_init(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		String::Utf8Value title(isolate, arg);
		int width = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int height = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int samples_per_pixel = args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		bool vertical_sync = args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int window_mode = args[5]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int window_features = args[6]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		// int api_version = args[7]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int x = -1;
		int y = -1;
		int frequency = 60;

		kinc_window_options_t win;
		win.title = *title;
		win.x = x;
		win.y = y;
		win.width = width;
		win.height = height;
		win.display_index = -1;
		#ifdef KORE_WINDOWS
		win.visible = false; // Prevent white flicker when opening the window
		#else
		win.visible = enable_window;
		#endif
		win.window_features = window_features;
		win.mode = (kinc_window_mode_t)window_mode;
		kinc_framebuffer_options_t frame;
		frame.frequency = frequency;
		frame.vertical_sync = vertical_sync;
		frame.color_bits = 32;
		frame.depth_bits = 0;
		frame.stencil_bits = 0;
		frame.samples_per_pixel = samples_per_pixel;
		kinc_init(*title, width, height, &win, &frame);
		kinc_random_init((int)(kinc_time() * 1000));

		#ifdef KORE_WINDOWS
		// Maximized window has x < -1, prevent window centering done by kinc
		if (x < -1 && y < -1) {
			kinc_window_move(0, x, y);
		}

		char vdata[4];
		DWORD cbdata = 4 * sizeof(char);
		RegGetValueW(HKEY_CURRENT_USER, L"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", L"AppsUseLightTheme", RRF_RT_REG_DWORD, nullptr, vdata, &cbdata);
		BOOL use_dark_mode = int(vdata[3] << 24 | vdata[2] << 16 | vdata[1] << 8 | vdata[0]) != 1;
		DwmSetWindowAttribute(kinc_windows_window_handle(0), DWMWA_USE_IMMERSIVE_DARK_MODE, &use_dark_mode, sizeof(use_dark_mode));

		show_window = true;
		#endif

		#ifdef WITH_AUDIO
		if (enable_audio) {
			kinc_mutex_init(&mutex);
			kinc_a1_init();
			kinc_a2_init();
			kinc_a2_set_callback(update_audio);
			audio_buffer.read_location = 0;
			audio_buffer.write_location = 0;
			audio_buffer.data_size = 128 * 1024;
			audio_buffer.data = new uint8_t[audio_buffer.data_size];
		}
		#endif

		kinc_set_update_callback(update, NULL);
		kinc_set_drop_files_callback(drop_files, NULL);
		kinc_set_copy_callback(copy, NULL);
		kinc_set_cut_callback(cut, NULL);
		kinc_set_paste_callback(paste, NULL);
		kinc_set_foreground_callback(foreground, NULL);
		kinc_set_resume_callback(resume, NULL);
		kinc_set_pause_callback(pause, NULL);
		kinc_set_background_callback(background, NULL);
		kinc_set_shutdown_callback(shutdown, NULL);

		kinc_keyboard_set_key_down_callback(key_down, NULL);
		kinc_keyboard_set_key_up_callback(key_up, NULL);
		kinc_keyboard_set_key_press_callback(key_press, NULL);
		kinc_mouse_set_move_callback(mouse_move, NULL);
		kinc_mouse_set_press_callback(mouse_down, NULL);
		kinc_mouse_set_release_callback(mouse_up, NULL);
		kinc_mouse_set_scroll_callback(mouse_wheel, NULL);
		kinc_surface_set_move_callback(touch_move);
		kinc_surface_set_touch_start_callback(touch_down);
		kinc_surface_set_touch_end_callback(touch_up);
		kinc_pen_set_press_callback(pen_down);
		kinc_pen_set_move_callback(pen_move);
		kinc_pen_set_release_callback(pen_up);
		kinc_gamepad_set_axis_callback(gamepad_axis);
		kinc_gamepad_set_button_callback(gamepad_button);
	}

	void krom_set_application_name(const FunctionCallbackInfo<Value> &args) {
		// Name used by kinc_internal_save_path()
		HandleScope scope(args.GetIsolate());
		String::Utf8Value name(isolate, args[0]);
		kinc_set_application_name(*name);
	}

	void krom_log(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		String::Utf8Value value(isolate, arg);
		size_t len = strlen(*value);
		if (len < 2048) {
			kinc_log(KINC_LOG_LEVEL_INFO, *value);
		}
		else {
			int pos = 0;
			while (pos < len) {
				strncpy(temp_string, *value + pos, 2047);
				temp_string[2047] = 0;
				kinc_log(KINC_LOG_LEVEL_INFO, temp_string);
				pos += 2047;
			}
		}
	}

	void krom_clear_fast(Local<Object> receiver, int flags, int color, float depth, int stencil) {
		kinc_g4_clear(flags, color, depth, stencil);
	}

	void krom_clear(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int flags = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int color = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float depth = (float)args[2]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int stencil = args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		krom_clear_fast(args.This(), flags, color, depth, stencil);
	}

	void krom_set_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		update_func.Reset(isolate, func);
	}

	void krom_set_drop_files_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		drop_files_func.Reset(isolate, func);
	}

	void krom_set_cut_copy_paste_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> cutArg = args[0];
		Local<Function> cutFunc = Local<Function>::Cast(cutArg);
		cut_func.Reset(isolate, cutFunc);
		Local<Value> copyArg = args[1];
		Local<Function> copyFunc = Local<Function>::Cast(copyArg);
		copy_func.Reset(isolate, copyFunc);
		Local<Value> pasteArg = args[2];
		Local<Function> pasteFunc = Local<Function>::Cast(pasteArg);
		paste_func.Reset(isolate, pasteFunc);
	}

	void krom_set_application_state_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> foregroundArg = args[0];
		Local<Function> foregroundFunc = Local<Function>::Cast(foregroundArg);
		foreground_func.Reset(isolate, foregroundFunc);
		Local<Value> resumeArg = args[1];
		Local<Function> resumeFunc = Local<Function>::Cast(resumeArg);
		resume_func.Reset(isolate, resumeFunc);
		Local<Value> pauseArg = args[2];
		Local<Function> pauseFunc = Local<Function>::Cast(pauseArg);
		pause_func.Reset(isolate, pauseFunc);
		Local<Value> backgroundArg = args[3];
		Local<Function> backgroundFunc = Local<Function>::Cast(backgroundArg);
		background_func.Reset(isolate, backgroundFunc);
		Local<Value> shutdownArg = args[4];
		Local<Function> shutdownFunc = Local<Function>::Cast(shutdownArg);
		shutdown_func.Reset(isolate, shutdownFunc);
	}

	void krom_set_keyboard_down_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		keyboard_down_func.Reset(isolate, func);
	}

	void krom_set_keyboard_up_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		keyboard_up_func.Reset(isolate, func);
	}

	void krom_set_keyboard_press_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		keyboard_press_func.Reset(isolate, func);
	}

	void krom_set_mouse_down_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		mouse_down_func.Reset(isolate, func);
	}

	void krom_set_mouse_up_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		mouse_up_func.Reset(isolate, func);
	}

	void krom_set_mouse_move_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		mouse_move_func.Reset(isolate, func);
	}

	void krom_set_touch_down_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		touch_down_func.Reset(isolate, func);
	}

	void krom_set_touch_up_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		touch_up_func.Reset(isolate, func);
	}

	void krom_set_touch_move_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		touch_move_func.Reset(isolate, func);
	}

	void krom_set_mouse_wheel_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		mouse_wheel_func.Reset(isolate, func);
	}

	void krom_set_pen_down_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		pen_down_func.Reset(isolate, func);
	}

	void krom_set_pen_up_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		pen_up_func.Reset(isolate, func);
	}

	void krom_set_pen_move_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		pen_move_func.Reset(isolate, func);
	}

	void krom_set_gamepad_axis_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		gamepad_axis_func.Reset(isolate, func);
	}

	void krom_set_gamepad_button_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		gamepad_button_func.Reset(isolate, func);
	}

	void krom_lock_mouse_fast(Local<Object> receiver) {
		kinc_mouse_lock(0);
	}

	void krom_lock_mouse(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		krom_lock_mouse_fast(args.This());
	}

	void krom_unlock_mouse_fast(Local<Object> receiver) {
		kinc_mouse_unlock();
	}

	void krom_unlock_mouse(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		krom_unlock_mouse_fast(args.This());
	}

	int krom_can_lock_mouse_fast(Local<Object> receiver) {
		return kinc_mouse_can_lock();
	}

	void krom_can_lock_mouse(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(Int32::New(isolate, krom_can_lock_mouse_fast(args.This())));
	}

	int krom_is_mouse_locked_fast(Local<Object> receiver) {
		return kinc_mouse_is_locked();
	}

	void krom_is_mouse_locked(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(Int32::New(isolate, krom_is_mouse_locked_fast(args.This())));
	}

	void krom_set_mouse_position_fast(Local<Object> receiver, int windowId, int x, int y) {
		kinc_mouse_set_position(windowId, x, y);
	}

	void krom_set_mouse_position(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int x = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int y = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		krom_set_mouse_position_fast(args.This(), windowId, x, y);
	}

	void krom_show_mouse_fast(Local<Object> receiver, int show) {
		show ? kinc_mouse_show() : kinc_mouse_hide();
	}

	void krom_show_mouse(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int show = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		krom_show_mouse_fast(args.This(), show);
	}

	void krom_show_keyboard_fast(Local<Object> receiver, int show) {
		show ? kinc_keyboard_show() : kinc_keyboard_hide();
	}

	void krom_show_keyboard(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int show = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		krom_show_keyboard_fast(args.This(), show);
	}

	void krom_create_indexbuffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);
		kinc_g4_index_buffer_t *buffer = (kinc_g4_index_buffer_t *)malloc(sizeof(kinc_g4_index_buffer_t));
		kinc_g4_index_buffer_init(buffer, args[0]->Int32Value(isolate->GetCurrentContext()).FromJust(), KINC_G4_INDEX_BUFFER_FORMAT_32BIT, KINC_G4_USAGE_STATIC);
		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, buffer));
		args.GetReturnValue().Set(obj);
	}

	void krom_delete_indexbuffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_index_buffer_t *buffer = (kinc_g4_index_buffer_t *)field->Value();
		kinc_g4_index_buffer_destroy(buffer);
		free(buffer);
	}

	void krom_lock_indexbuffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_index_buffer_t *buffer = (kinc_g4_index_buffer_t *)field->Value();
		int *vertices = (int *)kinc_g4_index_buffer_lock_all(buffer);
		std::unique_ptr<v8::BackingStore> backing = v8::ArrayBuffer::NewBackingStore((void *)vertices, kinc_g4_index_buffer_count(buffer) * sizeof(int), [](void *, size_t, void *) {}, nullptr);
		Local<ArrayBuffer> abuffer = ArrayBuffer::New(isolate, std::move(backing));
		args.GetReturnValue().Set(Uint32Array::New(abuffer, 0, kinc_g4_index_buffer_count(buffer)));
	}

	void krom_unlock_indexbuffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_index_buffer_t *buffer = (kinc_g4_index_buffer_t *)field->Value();
		kinc_g4_index_buffer_unlock_all(buffer);
	}

	void krom_set_indexbuffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_index_buffer_t *buffer = (kinc_g4_index_buffer_t *)field->Value();
		kinc_g4_set_index_buffer(buffer);
	}

	kinc_g4_vertex_data_t convert_vertex_data(int num) {
		switch (num) {
		case 0: // Float32_1X
			return KINC_G4_VERTEX_DATA_F32_1X;
		case 1: // Float32_2X
			return KINC_G4_VERTEX_DATA_F32_2X;
		case 2: // Float32_3X
			return KINC_G4_VERTEX_DATA_F32_3X;
		case 3: // Float32_4X
			return KINC_G4_VERTEX_DATA_F32_4X;
		case 4: // Float32_4X4
			return KINC_G4_VERTEX_DATA_F32_4X4;
		case 5: // Int8_1X
			return KINC_G4_VERTEX_DATA_I8_1X;
		case 6: // UInt8_1X
			return KINC_G4_VERTEX_DATA_U8_1X;
		case 7: // Int8_1X_Normalized
			return KINC_G4_VERTEX_DATA_I8_1X_NORMALIZED;
		case 8: // UInt8_1X_Normalized
			return KINC_G4_VERTEX_DATA_U8_1X_NORMALIZED;
		case 9: // Int8_2X
			return KINC_G4_VERTEX_DATA_I8_2X;
		case 10: // UInt8_2X
			return KINC_G4_VERTEX_DATA_U8_2X;
		case 11: // Int8_2X_Normalized
			return KINC_G4_VERTEX_DATA_I8_2X_NORMALIZED;
		case 12: // UInt8_2X_Normalized
			return KINC_G4_VERTEX_DATA_U8_2X_NORMALIZED;
		case 13: // Int8_4X
			return KINC_G4_VERTEX_DATA_I8_4X;
		case 14: // UInt8_4X
			return KINC_G4_VERTEX_DATA_U8_4X;
		case 15: // Int8_4X_Normalized
			return KINC_G4_VERTEX_DATA_I8_4X_NORMALIZED;
		case 16: // UInt8_4X_Normalized
			return KINC_G4_VERTEX_DATA_U8_4X_NORMALIZED;
		case 17: // Int16_1X
			return KINC_G4_VERTEX_DATA_I16_1X;
		case 18: // UInt16_1X
			return KINC_G4_VERTEX_DATA_U16_1X;
		case 19: // Int16_1X_Normalized
			return KINC_G4_VERTEX_DATA_I16_1X_NORMALIZED;
		case 20: // UInt16_1X_Normalized
			return KINC_G4_VERTEX_DATA_U16_1X_NORMALIZED;
		case 21: // Int16_2X
			return KINC_G4_VERTEX_DATA_I16_2X;
		case 22: // UInt16_2X
			return KINC_G4_VERTEX_DATA_U16_2X;
		case 23: // Int16_2X_Normalized
			return KINC_G4_VERTEX_DATA_I16_2X_NORMALIZED;
		case 24: // UInt16_2X_Normalized
			return KINC_G4_VERTEX_DATA_U16_2X_NORMALIZED;
		case 25: // Int16_4X
			return KINC_G4_VERTEX_DATA_I16_4X;
		case 26: // UInt16_4X
			return KINC_G4_VERTEX_DATA_U16_4X;
		case 27: // Int16_4X_Normalized
			return KINC_G4_VERTEX_DATA_I16_4X_NORMALIZED;
		case 28: // UInt16_4X_Normalized
			return KINC_G4_VERTEX_DATA_U16_4X_NORMALIZED;
		case 29: // Int32_1X
			return KINC_G4_VERTEX_DATA_I32_1X;
		case 30: // UInt32_1X
			return KINC_G4_VERTEX_DATA_U32_1X;
		case 31: // Int32_2X
			return KINC_G4_VERTEX_DATA_I32_2X;
		case 32: // UInt32_2X
			return KINC_G4_VERTEX_DATA_U32_2X;
		case 33: // Int32_3X
			return KINC_G4_VERTEX_DATA_I32_3X;
		case 34: // UInt32_3X
			return KINC_G4_VERTEX_DATA_U32_3X;
		case 35: // Int32_4X
			return KINC_G4_VERTEX_DATA_I32_4X;
		case 36: // UInt32_4X
			return KINC_G4_VERTEX_DATA_U32_4X;
		}
		return KINC_G4_VERTEX_DATA_NONE;
	}

	void krom_create_vertexbuffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);
		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		Local<Object> jsstructure = args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		int32_t length = jsstructure->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "length").ToLocalChecked()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_g4_vertex_structure_t structure;
		kinc_g4_vertex_structure_init(&structure);
		for (int32_t i = 0; i < length; ++i) {
			Local<Object> element = jsstructure->Get(isolate->GetCurrentContext(), i).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
			Local<Value> str = element->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked()).ToLocalChecked();
			String::Utf8Value utf8_value(isolate, str);
			int32_t data = element->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "data").ToLocalChecked()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
			strcpy(temp_string_vstruct[0][i], *utf8_value);
			kinc_g4_vertex_structure_add(&structure, temp_string_vstruct[0][i], convert_vertex_data(data));
		}
		kinc_g4_vertex_buffer_t *buffer = (kinc_g4_vertex_buffer_t *)malloc(sizeof(kinc_g4_vertex_buffer_t));
		kinc_g4_vertex_buffer_init(buffer, args[0]->Int32Value(isolate->GetCurrentContext()).FromJust(), &structure, (kinc_g4_usage_t)args[2]->Int32Value(isolate->GetCurrentContext()).FromJust(), args[3]->Int32Value(isolate->GetCurrentContext()).FromJust());
		obj->SetInternalField(0, External::New(isolate, buffer));
		args.GetReturnValue().Set(obj);
	}

	void krom_delete_vertexbuffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_vertex_buffer_t *buffer = (kinc_g4_vertex_buffer_t *)field->Value();
		kinc_g4_vertex_buffer_destroy(buffer);
		free(buffer);
	}

	void krom_lock_vertex_buffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_vertex_buffer_t *buffer = (kinc_g4_vertex_buffer_t *)field->Value();
		int start = args[1]->Int32Value(isolate->GetCurrentContext()).FromJust();
		int count = args[2]->Int32Value(isolate->GetCurrentContext()).FromJust();
		float *vertices = kinc_g4_vertex_buffer_lock(buffer, start, count);
		std::unique_ptr<v8::BackingStore> backing = v8::ArrayBuffer::NewBackingStore((void *)vertices, (uint32_t)(count * kinc_g4_vertex_buffer_stride(buffer)), [](void *, size_t, void *) {}, nullptr);
		Local<ArrayBuffer> abuffer = ArrayBuffer::New(isolate, std::move(backing));
		args.GetReturnValue().Set(abuffer);
	}

	void krom_unlock_vertex_buffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_vertex_buffer_t *buffer = (kinc_g4_vertex_buffer_t *)field->Value();
		int count = args[1]->Int32Value(isolate->GetCurrentContext()).FromJust();
		kinc_g4_vertex_buffer_unlock(buffer, count);
	}

	void krom_set_vertexbuffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_vertex_buffer_t *buffer = (kinc_g4_vertex_buffer_t *)field->Value();
		kinc_g4_set_vertex_buffer(buffer);
	}

	void krom_set_vertexbuffers(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		kinc_g4_vertex_buffer_t *vertex_buffers[8] = { nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr };
		Local<Object> jsarray = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		int32_t length = jsarray->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "length").ToLocalChecked()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		for (int32_t i = 0; i < length; ++i) {
			Local<Object> bufferobj = jsarray->Get(isolate->GetCurrentContext(), i).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "buffer").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
			Local<External> bufferfield = Local<External>::Cast(bufferobj->GetInternalField(0));
			kinc_g4_vertex_buffer_t *buffer = (kinc_g4_vertex_buffer_t *)bufferfield->Value();
			vertex_buffers[i] = buffer;
		}
		kinc_g4_set_vertex_buffers(vertex_buffers, length);
	}

	void krom_draw_indexed_vertices_fast(Local<Object> receiver, int start, int count) {
		if (count < 0) kinc_g4_draw_indexed_vertices();
		else kinc_g4_draw_indexed_vertices_from_to(start, count);
	}

	void krom_draw_indexed_vertices(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int start = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int count = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		krom_draw_indexed_vertices_fast(args.This(), start, count);
	}

	void krom_draw_indexed_vertices_instanced_fast(Local<Object> receiver, int instance_count, int start, int count) {
		if (count < 0) kinc_g4_draw_indexed_vertices_instanced(instance_count);
		else kinc_g4_draw_indexed_vertices_instanced_from_to(instance_count, start, count);
	}

	void krom_draw_indexed_vertices_instanced(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int instance_count = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int start = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int count = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		krom_draw_indexed_vertices_instanced_fast(args.This(), instance_count, start, count);
	}

	void krom_create_vertex_shader(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_g4_shader_t *shader = (kinc_g4_shader_t *)malloc(sizeof(kinc_g4_shader_t));
		kinc_g4_shader_init(shader, content->Data(), (int)content->ByteLength(), KINC_G4_SHADER_TYPE_VERTEX);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, shader));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked(), args[1]);
		args.GetReturnValue().Set(obj);
	}

	void krom_create_vertex_shader_from_source(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_value(isolate, args[0]);

		char *source = new char[strlen(*utf8_value) + 1];
		strcpy(source, *utf8_value);
		kinc_g4_shader_t *shader = (kinc_g4_shader_t *)malloc(sizeof(kinc_g4_shader_t));
		kinc_g4_shader_init(shader, source, strlen(source), KINC_G4_SHADER_TYPE_VERTEX);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, shader));
		Local<String> name = String::NewFromUtf8(isolate, "").ToLocalChecked();
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked(), name);
		args.GetReturnValue().Set(obj);
	}

	void krom_create_fragment_shader(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_g4_shader_t *shader = (kinc_g4_shader_t *)malloc(sizeof(kinc_g4_shader_t));
		kinc_g4_shader_init(shader, content->Data(), (int)content->ByteLength(), KINC_G4_SHADER_TYPE_FRAGMENT);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, shader));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked(), args[1]);
		args.GetReturnValue().Set(obj);
	}

	void krom_create_fragment_shader_from_source(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_value(isolate, args[0]);

		char *source = new char[strlen(*utf8_value) + 1];
		strcpy(source, *utf8_value);
		kinc_g4_shader_t *shader = (kinc_g4_shader_t *)malloc(sizeof(kinc_g4_shader_t));
		kinc_g4_shader_init(shader, source, strlen(source), KINC_G4_SHADER_TYPE_FRAGMENT);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, shader));
		Local<String> name = String::NewFromUtf8(isolate, "").ToLocalChecked();
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked(), name);
		args.GetReturnValue().Set(obj);
	}

	void krom_create_geometry_shader(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_g4_shader_t *shader = (kinc_g4_shader_t *)malloc(sizeof(kinc_g4_shader_t));
		kinc_g4_shader_init(shader, content->Data(), (int)content->ByteLength(), KINC_G4_SHADER_TYPE_GEOMETRY);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, shader));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked(), args[1]);
		args.GetReturnValue().Set(obj);
	}

	void krom_create_tessellation_control_shader(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_g4_shader_t *shader = (kinc_g4_shader_t *)malloc(sizeof(kinc_g4_shader_t));
		kinc_g4_shader_init(shader, content->Data(), (int)content->ByteLength(), KINC_G4_SHADER_TYPE_TESSELLATION_CONTROL);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, shader));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked(), args[1]);
		args.GetReturnValue().Set(obj);
	}

	void krom_create_tessellation_evaluation_shader(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_g4_shader_t *shader = (kinc_g4_shader_t *)malloc(sizeof(kinc_g4_shader_t));
		kinc_g4_shader_init(shader, content->Data(), (int)content->ByteLength(), KINC_G4_SHADER_TYPE_TESSELLATION_EVALUATION);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, shader));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked(), args[1]);
		args.GetReturnValue().Set(obj);
	}

	void krom_delete_shader(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_shader_t *shader = (kinc_g4_shader_t *)field->Value();
		kinc_g4_shader_destroy(shader);
		free(shader);
	}

	void krom_create_pipeline(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		kinc_g4_pipeline_t *pipeline = (kinc_g4_pipeline_t *)malloc(sizeof(kinc_g4_pipeline_t));
		kinc_g4_pipeline_init(pipeline);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(8);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, pipeline));
		args.GetReturnValue().Set(obj);
	}

	void krom_delete_pipeline(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Object> pipeobj = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<External> pipefield = Local<External>::Cast(pipeobj->GetInternalField(0));
		kinc_g4_pipeline_t *pipeline = (kinc_g4_pipeline_t *)pipefield->Value();
		kinc_g4_pipeline_destroy(pipeline);
		free(pipeline);
	}

	void krom_compile_pipeline(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());

		Local<Object> pipeobj = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();

		Local<External> pipefield = Local<External>::Cast(pipeobj->GetInternalField(0));
		kinc_g4_pipeline_t *pipeline = (kinc_g4_pipeline_t *)pipefield->Value();

		kinc_g4_vertex_structure_t s0, s1, s2, s3;
		kinc_g4_vertex_structure_init(&s0);
		kinc_g4_vertex_structure_init(&s1);
		kinc_g4_vertex_structure_init(&s2);
		kinc_g4_vertex_structure_init(&s3);
		kinc_g4_vertex_structure_t *structures[4] = { &s0, &s1, &s2, &s3 };

		int32_t size = args[5]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		for (int32_t i1 = 0; i1 < size; ++i1) {
			Local<Object> jsstructure = args[i1 + 1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
			structures[i1]->instanced = jsstructure->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "instanced").ToLocalChecked()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
			Local<Object> elements = jsstructure->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "elements").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
			int32_t length = elements->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "length").ToLocalChecked()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
			for (int32_t i2 = 0; i2 < length; ++i2) {
				Local<Object> element = elements->Get(isolate->GetCurrentContext(), i2).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
				Local<Value> str = element->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "name").ToLocalChecked()).ToLocalChecked();
				String::Utf8Value utf8_value(isolate, str);
				int32_t data = element->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "data").ToLocalChecked()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();

				strcpy(temp_string_vstruct[i1][i2], *utf8_value);
				kinc_g4_vertex_structure_add(structures[i1], temp_string_vstruct[i1][i2], convert_vertex_data(data));
			}
		}

		pipeobj->SetInternalField(1, External::New(isolate, structures));
		pipeobj->SetInternalField(2, External::New(isolate, &size));

		Local<External> vsfield = Local<External>::Cast(args[6]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_shader_t *vertexShader = (kinc_g4_shader_t *)vsfield->Value();
		pipeobj->SetInternalField(3, External::New(isolate, vertexShader));

		Local<External> fsfield = Local<External>::Cast(args[7]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_shader_t *fragmentShader = (kinc_g4_shader_t *)fsfield->Value();
		pipeobj->SetInternalField(4, External::New(isolate, fragmentShader));

		pipeline->vertex_shader = vertexShader;
		pipeline->fragment_shader = fragmentShader;

		if (!args[8]->IsNullOrUndefined()) {
			Local<External> gsfield = Local<External>::Cast(args[8]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
			kinc_g4_shader_t *geometryShader = (kinc_g4_shader_t *)gsfield->Value();
			pipeobj->SetInternalField(5, External::New(isolate, geometryShader));
			pipeline->geometry_shader = geometryShader;
		}

		if (!args[9]->IsNullOrUndefined()) {
			Local<External> tcsfield = Local<External>::Cast(args[9]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
			kinc_g4_shader_t *tessellationControlShader = (kinc_g4_shader_t *)tcsfield->Value();
			pipeobj->SetInternalField(6, External::New(isolate, tessellationControlShader));
			pipeline->tessellation_control_shader = tessellationControlShader;
		}

		if (!args[10]->IsNullOrUndefined()) {
			Local<External> tesfield = Local<External>::Cast(args[10]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
			kinc_g4_shader_t *tessellationEvaluationShader = (kinc_g4_shader_t *)tesfield->Value();
			pipeobj->SetInternalField(7, External::New(isolate, tessellationEvaluationShader));
			pipeline->tessellation_evaluation_shader = tessellationEvaluationShader;
		}

		for (int i = 0; i < size; ++i) {
			pipeline->input_layout[i] = structures[i];
		}
		pipeline->input_layout[size] = nullptr;

		Local<Object> args11 = args[11]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		pipeline->cull_mode = (kinc_g4_cull_mode_t)args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "cullMode").ToLocalChecked()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();

		pipeline->depth_write = args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "depthWrite").ToLocalChecked()).ToLocalChecked()->BooleanValue(isolate);
		pipeline->depth_mode = (kinc_g4_compare_mode_t)args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "depthMode").ToLocalChecked()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();

		pipeline->blend_source = (kinc_g4_blending_factor_t)args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "blendSource").ToLocalChecked()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		pipeline->blend_destination = (kinc_g4_blending_factor_t)args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "blendDestination").ToLocalChecked()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		pipeline->alpha_blend_source = (kinc_g4_blending_factor_t)args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "alphaBlendSource").ToLocalChecked()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		pipeline->alpha_blend_destination = (kinc_g4_blending_factor_t)args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "alphaBlendDestination").ToLocalChecked()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();

		Local<Object> maskRedArray = args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "colorWriteMaskRed").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<Object> maskGreenArray = args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "colorWriteMaskGreen").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<Object> maskBlueArray = args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "colorWriteMaskBlue").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<Object> maskAlphaArray = args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "colorWriteMaskAlpha").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();

		for (int i = 0; i < 8; ++i) {
			pipeline->color_write_mask_red[i] = maskRedArray->Get(isolate->GetCurrentContext(), i).ToLocalChecked()->BooleanValue(isolate);
			pipeline->color_write_mask_green[i] = maskGreenArray->Get(isolate->GetCurrentContext(), i).ToLocalChecked()->BooleanValue(isolate);
			pipeline->color_write_mask_blue[i] = maskBlueArray->Get(isolate->GetCurrentContext(), i).ToLocalChecked()->BooleanValue(isolate);
			pipeline->color_write_mask_alpha[i] = maskAlphaArray->Get(isolate->GetCurrentContext(), i).ToLocalChecked()->BooleanValue(isolate);
		}

		pipeline->conservative_rasterization = args11->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "conservativeRasterization").ToLocalChecked()).ToLocalChecked()->BooleanValue(isolate);

		kinc_g4_pipeline_compile(pipeline);
	}

	void krom_set_pipeline(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Object> pipeobj = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<External> pipefield = Local<External>::Cast(pipeobj->GetInternalField(0));
		kinc_g4_pipeline_t *pipeline = (kinc_g4_pipeline_t *)pipefield->Value();
		kinc_g4_set_pipeline(pipeline);
	}

	bool ends_with(const char *str, const char *suffix) {
		if (!str || !suffix) return 0;
		size_t lenstr = strlen(str);
		size_t lensuffix = strlen(suffix);
		if (lensuffix > lenstr) return 0;
		return strncmp(str + lenstr - lensuffix, suffix, lensuffix) == 0;
	}

	bool load_image(kinc_file_reader_t &reader, const char *filename, unsigned char *&output, int &width, int &height, kinc_image_format_t &format) {
		format = KINC_IMAGE_FORMAT_RGBA32;
		int size = (int)kinc_file_reader_size(&reader);
		int comp;
		bool success = true;
		unsigned char *data = (unsigned char *)malloc(size);
		kinc_file_reader_read(&reader, data, size);
		kinc_file_reader_close(&reader);

		if (ends_with(filename, "k")) {
			width = kinc_read_s32le(data);
			height = kinc_read_s32le(data + 4);
			char fourcc[5];
			fourcc[0] = data[8];
			fourcc[1] = data[9];
			fourcc[2] = data[10];
			fourcc[3] = data[11];
			fourcc[4] = 0;
			int compressedSize = size - 12;
			if (strcmp(fourcc, "LZ4 ") == 0) {
				int outputSize = width * height * 4;
				output = (unsigned char *)malloc(outputSize);
				LZ4_decompress_safe((char *)(data + 12), (char *)output, compressedSize, outputSize);
			}
			else if (strcmp(fourcc, "LZ4F") == 0) {
				int outputSize = width * height * 16;
				output = (unsigned char *)malloc(outputSize);
				LZ4_decompress_safe((char *)(data + 12), (char *)output, compressedSize, outputSize);
				format = KINC_IMAGE_FORMAT_RGBA128;
			}
			else {
				success = false;
			}
		}
		else if (ends_with(filename, "hdr")) {
			output = (unsigned char *)stbi_loadf_from_memory(data, size, &width, &height, &comp, 4);
			if (output == nullptr) {
				kinc_log(KINC_LOG_LEVEL_ERROR, stbi_failure_reason());
				success = false;
			}
			format = KINC_IMAGE_FORMAT_RGBA128;
		}
		else { // jpg, png, ..
			output = stbi_load_from_memory(data, size, &width, &height, &comp, 4);
			if (output == nullptr) {
				kinc_log(KINC_LOG_LEVEL_ERROR, stbi_failure_reason());
				success = false;
			}
		}
		free(data);
		return success;
	}

	void krom_load_image(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_value(isolate, args[0]);
		bool readable = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		bool success = true;

		kinc_image_t *image = (kinc_image_t *)malloc(sizeof(kinc_image_t));

		// if (armorcore) {
			kinc_file_reader_t reader;
			if (kinc_file_reader_open(&reader, *utf8_value, KINC_FILE_TYPE_ASSET)) {
				unsigned char *image_data;
				int image_width;
				int image_height;
				kinc_image_format_t image_format;
				success = load_image(reader, *utf8_value, image_data, image_width, image_height, image_format);
				if (success) {
					kinc_image_init(image, image_data, image_width, image_height, image_format);
				}
			}
			else {
				success = false;
			}
		// }
		// else {
		// 	// TODO: make kinc_image load faster
		// 	size_t byte_size = kinc_image_size_from_file(*utf8_value);
		// 	if (byte_size == 0) {
		// 		success = false;
		// 	}
		// 	else {
		// 		void *memory = malloc(byte_size);
		// 		kinc_image_init_from_file(image, memory, *utf8_value);
		// 	}
		// }

		if (!success) {
			free(image);
			return;
		}

		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)malloc(sizeof(kinc_g4_texture_t));
		kinc_g4_texture_init_from_image(texture, image);
		if (!readable) {
			free(image->data);
			kinc_image_destroy(image);
			free(image);
			// free(memory);
		}

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(readable ? 2 : 1);
		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, texture));
		if (readable) obj->SetInternalField(1, External::New(isolate, image));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "width").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "height").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "realWidth").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "realHeight").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		args.GetReturnValue().Set(obj);
	}

	void krom_unload_image(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		if (args[0]->IsNullOrUndefined()) return;
		Local<Object> image = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<Value> tex = image->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "texture_").ToLocalChecked()).ToLocalChecked();
		Local<Value> rt = image->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "renderTarget_").ToLocalChecked()).ToLocalChecked();

		if (tex->IsObject()) {
			Local<External> texfield = Local<External>::Cast(tex->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
			kinc_g4_texture_t *texture = (kinc_g4_texture_t *)texfield->Value();
			kinc_g4_texture_destroy(texture);
			free(texture);
		}
		else if (rt->IsObject()) {
			Local<External> rtfield = Local<External>::Cast(rt->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
			kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)rtfield->Value();
			kinc_g4_render_target_destroy(render_target);
			free(render_target);
		}
	}

	#ifdef WITH_AUDIO
	void krom_set_audio_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		audio_func.Reset(isolate, func);
	}

	void krom_audio_thread(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		bool lock = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		if (lock) kinc_mutex_lock(&mutex);    //Locker::Locker(isolate);
		else kinc_mutex_unlock(&mutex);       //Unlocker(args.GetIsolate());
	}

	void krom_load_sound(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_value(isolate, args[0]);
		kinc_a1_sound_t *sound = kinc_a1_sound_create(*utf8_value);

		if (sound == nullptr) {
			return;
		}

		Local<ArrayBuffer> buffer = ArrayBuffer::New(isolate, sound->size * 2 * sizeof(float));
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		float *to = (float *)content->Data();

		int16_t *left = (int16_t *)&sound->left[0];
		int16_t *right = (int16_t *)&sound->right[0];
		for (int i = 0; i < sound->size; i += 1) {
			to[i * 2    ] = (float)(left [i] / 32767.0);
			to[i * 2 + 1] = (float)(right[i] / 32767.0);
		}
		args.GetReturnValue().Set(buffer);
		kinc_a1_sound_destroy(sound);
	}

	void krom_write_audio_buffer(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		int samples = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();

		for (int i = 0; i < samples; ++i) {
			float *values = (float *)content->Data();
			float value = values[audio_read_location / 4];
			audio_read_location += 4;
			if (audio_read_location >= content->ByteLength()) audio_read_location = 0;
			*(float *)&audio_buffer.data[audio_buffer.write_location] = value;
			audio_buffer.write_location += 4;
			if (audio_buffer.write_location >= audio_buffer.data_size) audio_buffer.write_location = 0;
		}
	}

	int krom_get_samples_per_second_fast(Local<Object> receiver) {
		kinc_log(KINC_LOG_LEVEL_INFO, "Samples per second: %d Hz.", kinc_a2_samples_per_second);
		return kinc_a2_samples_per_second;
	}

	void krom_get_samples_per_second(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(Int32::New(isolate, krom_get_samples_per_second_fast(args.This())));
	}

	void update_audio(kinc_a2_buffer_t *buffer, int samples) {
		// kinc_mutex_lock(&mutex);
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		MicrotasksScope microtasks_scope(isolate, MicrotasksScope::kRunMicrotasks);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, audio_func);
		Local<Value> result;
		const int argc = 1;
		Local<Value> argv[argc] = {Int32::New(isolate, samples)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}

		for (int i = 0; i < samples; ++i) {
			float sample = *(float *)&audio_buffer.data[audio_buffer.read_location];
			audio_buffer.read_location += 4;
			if (audio_buffer.read_location >= audio_buffer.data_size) {
				audio_buffer.read_location = 0;
			}

			*(float *)&buffer->data[buffer->write_location] = sample;
			buffer->write_location += 4;
			if (buffer->write_location >= buffer->data_size) {
				buffer->write_location = 0;
			}
		}

		// kinc_mutex_unlock(&mutex);
	}

	#else

	void krom_set_audio_callback(const FunctionCallbackInfo<Value> &args) {
	}

	void krom_audio_thread(const FunctionCallbackInfo<Value> &args) {
	}

	void krom_load_sound(const FunctionCallbackInfo<Value> &args) {
	}

	void krom_write_audio_buffer(const FunctionCallbackInfo<Value> &args) {
	}

	void krom_get_samples_per_second(const FunctionCallbackInfo<Value> &args) {
	}

	#endif

	void krom_load_blob(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_value(isolate, args[0]);

		kinc_file_reader_t reader;
		if (!kinc_file_reader_open(&reader, *utf8_value, KINC_FILE_TYPE_ASSET)) return;
		uint32_t reader_size = (uint32_t)kinc_file_reader_size(&reader);

		Local<ArrayBuffer> buffer = ArrayBuffer::New(isolate, reader_size);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_file_reader_read(&reader, content->Data(), reader_size);
		kinc_file_reader_close(&reader);

		args.GetReturnValue().Set(buffer);
	}

	void krom_load_url(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_value(isolate, args[0]);
		kinc_load_url(*utf8_value);
	}

	void krom_copy_to_clipboard(const FunctionCallbackInfo<Value>& args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_value(isolate, args[0]);
		kinc_copy_to_clipboard(*utf8_value);
	}

	void krom_get_constant_location(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> pipefield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_pipeline_t *pipeline = (kinc_g4_pipeline_t *)pipefield->Value();

		String::Utf8Value utf8_value(isolate, args[1]);
		kinc_g4_constant_location_t location = kinc_g4_pipeline_get_constant_location(pipeline, *utf8_value);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		kinc_g4_constant_location_t *location_copy = (kinc_g4_constant_location_t *)malloc(sizeof(kinc_g4_constant_location_t));
		memcpy(location_copy, &location, sizeof(kinc_g4_constant_location_t)); // TODO
		obj->SetInternalField(0, External::New(isolate, location_copy));
		args.GetReturnValue().Set(obj);
	}

	void krom_get_texture_unit(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> pipefield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_pipeline_t *pipeline = (kinc_g4_pipeline_t *)pipefield->Value();

		String::Utf8Value utf8_value(isolate, args[1]);
		kinc_g4_texture_unit_t unit = kinc_g4_pipeline_get_texture_unit(pipeline, *utf8_value);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		kinc_g4_texture_unit_t *unit_copy = (kinc_g4_texture_unit_t *)malloc(sizeof(kinc_g4_texture_unit_t));
		memcpy(unit_copy, &unit, sizeof(kinc_g4_texture_unit_t)); // TODO
		obj->SetInternalField(0, External::New(isolate, unit_copy));
		args.GetReturnValue().Set(obj);
	}

	void krom_set_texture(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_unit_t *unit = (kinc_g4_texture_unit_t *)unitfield->Value();
		Local<External> texfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)texfield->Value();
		kinc_g4_set_texture(*unit, texture);
	}

	void krom_set_render_target(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_unit_t *unit = (kinc_g4_texture_unit_t *)unitfield->Value();
		Local<External> rtfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)rtfield->Value();
		kinc_g4_render_target_use_color_as_texture(render_target, *unit);
	}

	void krom_set_texture_depth(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_unit_t *unit = (kinc_g4_texture_unit_t *)unitfield->Value();
		Local<External> rtfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)rtfield->Value();
		kinc_g4_render_target_use_depth_as_texture(render_target, *unit);
	}

	void krom_set_image_texture(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_unit_t *unit = (kinc_g4_texture_unit_t *)unitfield->Value();
		Local<External> texfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)texfield->Value();
		kinc_g4_set_image_texture(*unit, texture);
	}

	void krom_set_texture_parameters(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_unit_t *unit = (kinc_g4_texture_unit_t *)unitfield->Value();
		kinc_g4_set_texture_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_U, (kinc_g4_texture_addressing_t)args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_V, (kinc_g4_texture_addressing_t)args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture_minification_filter(*unit, (kinc_g4_texture_filter_t)args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture_magnification_filter(*unit, (kinc_g4_texture_filter_t)args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture_mipmap_filter(*unit, (kinc_g4_mipmap_filter_t)args[5]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
	}

	void krom_set_texture3d_parameters(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_unit_t *unit = (kinc_g4_texture_unit_t *)unitfield->Value();
		kinc_g4_set_texture3d_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_U, (kinc_g4_texture_addressing_t)args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture3d_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_V, (kinc_g4_texture_addressing_t)args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture3d_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_W, (kinc_g4_texture_addressing_t)args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture3d_minification_filter(*unit, (kinc_g4_texture_filter_t)args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture3d_magnification_filter(*unit, (kinc_g4_texture_filter_t)args[5]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_g4_set_texture3d_mipmap_filter(*unit, (kinc_g4_mipmap_filter_t)args[6]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
	}

	void krom_set_texture_compare_mode(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_unit_t *unit = (kinc_g4_texture_unit_t *)unitfield->Value();
		kinc_g4_set_texture_compare_mode(*unit, args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());
	}

	void krom_set_cube_map_compare_mode(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_unit_t *unit = (kinc_g4_texture_unit_t *)unitfield->Value();
		kinc_g4_set_cubemap_compare_mode(*unit, args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());
	}

	void krom_set_bool(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();
		int32_t value = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_g4_set_bool(*location, value != 0);
	}

	void krom_set_int(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();
		int32_t value = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_g4_set_int(*location, value);
	}

	void krom_set_float(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();
		float value = (float)args[1]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_g4_set_float(*location, value);
	}

	void krom_set_float2(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();
		float value1 = (float)args[1]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value2 = (float)args[2]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_g4_set_float2(*location, value1, value2);
	}

	void krom_set_float3(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();
		float value1 = (float)args[1]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value2 = (float)args[2]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value3 = (float)args[3]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_g4_set_float3(*location, value1, value2, value3);
	}

	void krom_set_float4(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();
		float value1 = (float)args[1]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value2 = (float)args[2]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value3 = (float)args[3]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value4 = (float)args[4]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_g4_set_float4(*location, value1, value2, value3, value4);
	}

	void krom_set_floats(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();

		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();

		float *from = (float *)content->Data();
		kinc_g4_set_floats(*location, from, int(content->ByteLength() / 4));
	}

	void krom_set_matrix(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();

		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		float *from = (float *)content->Data();
		kinc_g4_set_matrix4(*location, (kinc_matrix4x4_t *)from);
	}

	void krom_set_matrix3(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_constant_location_t *location = (kinc_g4_constant_location_t *)locationfield->Value();

		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		float *from = (float *)content->Data();
		kinc_g4_set_matrix3(*location, (kinc_matrix3x3_t *)from);
	}

	double krom_get_time_fast(Local<Object> receiver) {
		return kinc_time();
	}

	void krom_get_time(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(Number::New(isolate, krom_get_time_fast(args.This())));
	}

	int krom_window_width_fast(Local<Object> receiver, int windowId) {
		return kinc_window_width(windowId);
	}

	void krom_window_width(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, krom_window_width_fast(args.This(), windowId)));
	}

	int krom_window_height_fast(Local<Object> receiver, int windowId) {
		return kinc_window_height(windowId);
	}

	void krom_window_height(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, krom_window_height_fast(args.This(), windowId)));
	}

	void krom_set_window_title(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		String::Utf8Value title(isolate, args[1]);
		kinc_window_set_title(windowId, *title);
	}

	void krom_get_window_mode(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, kinc_window_get_mode(windowId)));
	}

	void krom_set_window_mode(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_window_mode_t windowMode = (kinc_window_mode_t)args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_window_change_mode(windowId, windowMode);
	}

	void krom_resize_window(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int width = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int height = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_window_resize(windowId, width, height);
	}

	void krom_move_window(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int x = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int y = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_window_move(windowId, x, y);
	}

	void krom_screen_dpi(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int ppi = kinc_display_current_mode(kinc_primary_display()).pixels_per_inch;
		args.GetReturnValue().Set(Int32::New(isolate, ppi));
	}

	void krom_system_id(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(String::NewFromUtf8(isolate, kinc_system_id()).ToLocalChecked());
	}

	void krom_request_shutdown(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		kinc_stop();
	}

	void krom_display_count(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(Int32::New(isolate, kinc_count_displays()));
	}

	void krom_display_width(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int index = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, kinc_display_current_mode(index).width));
	}

	void krom_display_height(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int index = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, kinc_display_current_mode(index).height));
	}

	void krom_display_x(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int index = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, kinc_display_current_mode(index).x));
	}

	void krom_display_y(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int index = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, kinc_display_current_mode(index).y));
	}

	void krom_display_frequency(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int index = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, kinc_display_current_mode(index).frequency));
	}

	void krom_display_is_primary(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int index = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		#ifdef KORE_LINUX // TODO: Primary display detection broken in Kinc
		args.GetReturnValue().Set(Int32::New(isolate, true));
		#else
		args.GetReturnValue().Set(Int32::New(isolate, index == kinc_primary_display()));
		#endif
	}

	void krom_write_storage(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_name(isolate, args[0]);

		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();

		kinc_file_writer_t writer;
		kinc_file_writer_open(&writer, *utf8_name);
		kinc_file_writer_write(&writer, content->Data(), (int)content->ByteLength());
		kinc_file_writer_close(&writer);
	}

	void krom_read_storage(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_name(isolate, args[0]);

		kinc_file_reader_t reader;
		if (!kinc_file_reader_open(&reader, *utf8_name, KINC_FILE_TYPE_SAVE)) return;
		int reader_size = (int)kinc_file_reader_size(&reader);

		Local<ArrayBuffer> buffer = ArrayBuffer::New(isolate, reader_size);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_file_reader_read(&reader, content->Data(), reader_size);
		kinc_file_reader_close(&reader);

		args.GetReturnValue().Set(buffer);
	}

	void krom_create_render_target(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)malloc(sizeof(kinc_g4_render_target_t));
		kinc_g4_render_target_init(render_target, args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), (kinc_g4_render_target_format_t)args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, render_target));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "width").ToLocalChecked(), Int32::New(isolate, render_target->width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "height").ToLocalChecked(), Int32::New(isolate, render_target->height));
		args.GetReturnValue().Set(obj);
	}

	void krom_create_render_target_cube_map(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)malloc(sizeof(kinc_g4_render_target_t));
		kinc_g4_render_target_init_cube(render_target, args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), (kinc_g4_render_target_format_t)args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, render_target));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "width").ToLocalChecked(), Int32::New(isolate, render_target->width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "height").ToLocalChecked(), Int32::New(isolate, render_target->height));
		args.GetReturnValue().Set(obj);
	}

	void krom_create_texture(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)malloc(sizeof(kinc_g4_texture_t));
		kinc_g4_texture_init(texture, args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), (kinc_image_format_t)args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, texture));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "width").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "height").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "realWidth").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "realHeight").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		args.GetReturnValue().Set(obj);
	}

	void krom_create_texture3d(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)malloc(sizeof(kinc_g4_texture_t));
		kinc_g4_texture_init3d(texture, args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), (kinc_image_format_t)args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, texture));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "width").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "height").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "depth").ToLocalChecked(), Int32::New(isolate, texture->tex_depth));
		args.GetReturnValue().Set(obj);
	}

	void krom_create_texture_from_bytes(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)malloc(sizeof(kinc_g4_texture_t));
		kinc_image_t *image = (kinc_image_t *)malloc(sizeof(kinc_image_t));

		bool readable = args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		void *image_data;
		if (readable) {
			image_data = malloc(content->ByteLength());
			memcpy(image_data, content->Data(), content->ByteLength());
		}
		else {
			image_data = content->Data();
		}

		kinc_image_init(image, image_data, args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), (kinc_image_format_t)args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());
		kinc_g4_texture_init_from_image(texture, image);

		if (!readable) {
			kinc_image_destroy(image);
			free(image);
		}

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(readable ? 2 : 1);
		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, texture));
		if (readable) obj->SetInternalField(1, External::New(isolate, image));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "width").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "height").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "realWidth").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "realHeight").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		args.GetReturnValue().Set(obj);
	}

	void krom_create_texture_from_bytes3d(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)malloc(sizeof(kinc_g4_texture_t));
		kinc_image_t *image = (kinc_image_t*)malloc(sizeof(kinc_image_t));

		bool readable = args[5]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		void *image_data;
		if (readable) {
			image_data = malloc(content->ByteLength());
			memcpy(image_data, content->Data(), content->ByteLength());
		}
		else {
			image_data = content->Data();
		}

		kinc_image_init3d(image, image_data, args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value(), (kinc_image_format_t)args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());
		kinc_g4_texture_init_from_image3d(texture, image);

		if (!readable) {
			kinc_image_destroy(image);
			free(image);
		}

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(readable ? 2 : 1);
		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, texture));
		if (readable) obj->SetInternalField(1, External::New(isolate, image));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "width").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "height").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "depth").ToLocalChecked(), Int32::New(isolate, texture->tex_depth));
		args.GetReturnValue().Set(obj);
	}

	void krom_create_texture_from_encoded_bytes(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		String::Utf8Value format(isolate, args[1]);
		bool readable = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();

		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)malloc(sizeof(kinc_g4_texture_t));
		kinc_image_t *image = (kinc_image_t *)malloc(sizeof(kinc_image_t));

		unsigned char *content_data = (unsigned char *)content->Data();
		int content_length = (int)content->ByteLength();
		unsigned char *image_data;
		kinc_image_format_t image_format;
		int image_width;
		int image_height;

		if (ends_with(*format, "k")) {
			image_width = kinc_read_s32le(content_data);
			image_height = kinc_read_s32le(content_data + 4);
			char fourcc[5];
			fourcc[0] = content_data[8];
			fourcc[1] = content_data[9];
			fourcc[2] = content_data[10];
			fourcc[3] = content_data[11];
			fourcc[4] = 0;
			int compressedSize = (int)content->ByteLength() - 12;
			if (strcmp(fourcc, "LZ4 ") == 0) {
				int outputSize = image_width * image_height * 4;
				image_data = (unsigned char *)malloc(outputSize);
				LZ4_decompress_safe((char *)content_data + 12, (char *)image_data, compressedSize, outputSize);
				image_format = KINC_IMAGE_FORMAT_RGBA32;
			}
			else if (strcmp(fourcc, "LZ4F") == 0) {
				int outputSize = image_width * image_height * 16;
				image_data = (unsigned char *)malloc(outputSize);
				LZ4_decompress_safe((char *)content_data + 12, (char *)image_data, compressedSize, outputSize);
				image_format = KINC_IMAGE_FORMAT_RGBA128;
			}
		}
		else if (ends_with(*format, "hdr")) {
			int comp;
			image_data = (unsigned char *)stbi_loadf_from_memory(content_data, content_length, &image_width, &image_height, &comp, 4);
			image_format = KINC_IMAGE_FORMAT_RGBA128;
		}
		else { // jpg, png, ..
			int comp;
			image_data = stbi_load_from_memory(content_data, content_length, &image_width, &image_height, &comp, 4);
			image_format = KINC_IMAGE_FORMAT_RGBA32;
		}

		kinc_image_init(image, image_data, image_width, image_height, image_format);
		kinc_g4_texture_init_from_image(texture, image);
		if (!readable) {
			free(image->data);
			kinc_image_destroy(image);
			free(image);
		}

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(readable ? 2 : 1);
		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, texture));
		if (readable) obj->SetInternalField(1, External::New(isolate, image));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "width").ToLocalChecked(), Int32::New(isolate, texture->tex_width));
		(void) obj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "height").ToLocalChecked(), Int32::New(isolate, texture->tex_height));
		args.GetReturnValue().Set(obj);
	}

	int format_byte_size(kinc_image_format_t format) {
		switch (format) {
		case KINC_IMAGE_FORMAT_RGBA128:
			return 16;
		case KINC_IMAGE_FORMAT_RGBA64:
			return 8;
		case KINC_IMAGE_FORMAT_RGB24:
			return 4;
		case KINC_IMAGE_FORMAT_A32:
			return 4;
		case KINC_IMAGE_FORMAT_A16:
			return 2;
		case KINC_IMAGE_FORMAT_GREY8:
			return 1;
		case KINC_IMAGE_FORMAT_BGRA32:
		case KINC_IMAGE_FORMAT_RGBA32:
		default:
			return 4;
		}
	}

	void krom_get_texture_pixels(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());

		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(1));
		kinc_image_t *image = (kinc_image_t *)field->Value();

		uint8_t *data = kinc_image_get_pixels(image);
		int byteLength = format_byte_size(image->format) * image->width * image->height * image->depth;
		std::unique_ptr<v8::BackingStore> backing = v8::ArrayBuffer::NewBackingStore((void *)data, byteLength, [](void *, size_t, void *) {}, nullptr);
		Local<ArrayBuffer> buffer = ArrayBuffer::New(isolate, std::move(backing));
		args.GetReturnValue().Set(buffer);
	}

	void krom_get_render_target_pixels(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());

		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *rt = (kinc_g4_render_target_t *)field->Value();

		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();

		uint8_t *b = (uint8_t *)content->Data();
		kinc_g4_render_target_get_pixels(rt, b);
	}

	void krom_lock_texture(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Object> textureobj = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<External> field = Local<External>::Cast(textureobj->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)field->Value();
		uint8_t *tex = kinc_g4_texture_lock(texture);

		int stride = kinc_g4_texture_stride(texture);
		(void) textureobj->Set(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "stride").ToLocalChecked(), Int32::New(isolate, stride));

		int byteLength = stride * texture->tex_height * texture->tex_depth;
		std::unique_ptr<v8::BackingStore> backing = v8::ArrayBuffer::NewBackingStore((void *)tex, byteLength, [](void *, size_t, void *) {}, nullptr);
		Local<ArrayBuffer> abuffer = ArrayBuffer::New(isolate, std::move(backing));
		args.GetReturnValue().Set(abuffer);
	}

	void krom_unlock_texture(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)field->Value();
		kinc_g4_texture_unlock(texture);
	}

	void krom_clear_texture(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)field->Value();
		int x = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int y = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int z = args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int width = args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int height = args[5]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int depth = args[6]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int color = args[7]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_g4_texture_clear(texture, x, y, z, width, height, depth, color);
	}

	void krom_generate_texture_mipmaps(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)field->Value();
		kinc_g4_texture_generate_mipmaps(texture, args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());
	}

	void krom_generate_render_target_mipmaps(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *rt = (kinc_g4_render_target_t *)field->Value();
		kinc_g4_render_target_generate_mipmaps(rt, args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value());
	}

	void krom_set_mipmaps(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> field = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)field->Value();

		Local<Object> jsarray = args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		int32_t length = jsarray->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "length").ToLocalChecked()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		for (int32_t i = 0; i < length; ++i) {
			Local<Object> mipmapobj = jsarray->Get(isolate->GetCurrentContext(), i).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "texture_").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
			Local<External> mipmapfield = Local<External>::Cast(mipmapobj->GetInternalField(1));
			kinc_image_t *mipmap = (kinc_image_t *)mipmapfield->Value();
			kinc_g4_texture_set_mipmap(texture, mipmap, i + 1);
		}
	}

	void krom_set_depth_stencil_from(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> targetfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)targetfield->Value();
		Local<External> sourcefield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *source_target = (kinc_g4_render_target_t *)sourcefield->Value();
		kinc_g4_render_target_set_depth_stencil_from(render_target, source_target);
	}

	void krom_viewport_fast(Local<Object> receiver, int x, int y, int w, int h) {
		kinc_g4_viewport(x, y, w, h);
	}

	void krom_viewport(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int x = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		int y = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		int w = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		int h = args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		krom_viewport_fast(args.This(), x, y, w, h);
	}

	void krom_scissor_fast(Local<Object> receiver, int x, int y, int w, int h) {
		kinc_g4_scissor(x, y, w, h);
	}

	void krom_scissor(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int x = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		int y = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		int w = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		int h = args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		krom_scissor_fast(args.This(), x, y, w, h);
	}

	void krom_disable_scissor_fast(Local<Object> receiver) {
		kinc_g4_disable_scissor();
	}

	void krom_disable_scissor(const FunctionCallbackInfo<Value> &args) {
		krom_disable_scissor_fast(args.This());
	}

	int krom_render_targets_inverted_y_fast(Local<Object> receiver) {
		return kinc_g4_render_targets_inverted_y();
	}

	void krom_render_targets_inverted_y(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(Int32::New(isolate, krom_render_targets_inverted_y_fast(args.This())));
	}

	void krom_begin(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		if (args[0]->IsNullOrUndefined()) {
			kinc_g4_restore_render_target();
		}
		else {
			Local<Object> obj = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "renderTarget_").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
			Local<External> rtfield = Local<External>::Cast(obj->GetInternalField(0));
			kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)rtfield->Value();

			int32_t length = 1;
			kinc_g4_render_target_t *render_targets[8] = { render_target, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr };
			if (!args[1]->IsNullOrUndefined()) {
				Local<Object> jsarray = args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
				length = jsarray->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "length").ToLocalChecked()).ToLocalChecked()->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value() + 1;
				if (length > 8) length = 8;
				for (int32_t i = 1; i < length; ++i) {
					Local<Object> artobj = jsarray->Get(isolate->GetCurrentContext(), i - 1).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "renderTarget_").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
					Local<External> artfield = Local<External>::Cast(artobj->GetInternalField(0));
					kinc_g4_render_target_t *art = (kinc_g4_render_target_t *)artfield->Value();
					render_targets[i] = art;
				}
			}
			kinc_g4_set_render_targets(render_targets, length);
		}
	}

	void krom_begin_face(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Object> obj = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "renderTarget_").ToLocalChecked()).ToLocalChecked()->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<External> rtfield = Local<External>::Cast(obj->GetInternalField(0));
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)rtfield->Value();
		int face = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		kinc_g4_set_render_target_face(render_target, face);
	}

	void krom_end(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
	}

	void krom_file_save_bytes(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_path(isolate, args[0]);

		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();

		bool hasLengthArg = args.Length() > 2 && !args[2]->IsNullOrUndefined();
		int byteLength = hasLengthArg ? args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value() : (int)content->ByteLength();
		if (byteLength > (int)content->ByteLength()) byteLength = (int)content->ByteLength();

		#ifdef KORE_WINDOWS
		MultiByteToWideChar(CP_UTF8, 0, *utf8_path, -1, temp_wstring, 1024);
		FILE *file = _wfopen(temp_wstring, L"wb");
		#else
		FILE *file = fopen(*utf8_path, "wb");
		#endif
		if (file == nullptr) return;
		fwrite(content->Data(), 1, byteLength, file);
		fclose(file);
	}

	int sys_command(const char *cmd) {
		#ifdef KORE_WINDOWS
		int wlen = MultiByteToWideChar(CP_UTF8, 0, cmd, -1, NULL, 0);
		wchar_t *wstr = new wchar_t[wlen];
		MultiByteToWideChar(CP_UTF8, 0, cmd, -1, wstr, wlen);
		int result = _wsystem(wstr);
		delete[] wstr;
		#else
		int result = system(cmd);
		#endif
		return result;
	}

	void krom_sys_command(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_cmd(isolate, args[0]);
		int result = sys_command(*utf8_cmd);
		args.GetReturnValue().Set(Int32::New(isolate, result));
	}

	void krom_save_path(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(String::NewFromUtf8(isolate, kinc_internal_save_path()).ToLocalChecked());
	}

	void krom_get_arg_count(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(Int32::New(isolate, _argc));
	}

	void krom_get_arg(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int index = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(String::NewFromUtf8(isolate, _argv[index]).ToLocalChecked());
	}

	void krom_get_files_location(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		#ifdef KORE_MACOS
		char path[1024];
		strcpy(path, macgetresourcepath());
		strcat(path, "/");
		strcat(path, KORE_DEBUGDIR);
		strcat(path, "/");
		args.GetReturnValue().Set(String::NewFromUtf8(isolate, path).ToLocalChecked());
		#else
		args.GetReturnValue().Set(String::NewFromUtf8(isolate, kinc_internal_get_files_location()).ToLocalChecked());
		#endif
	}

	void krom_http_callback(int error, int response, const char *body, void *callbackdata) {
		#if defined(KORE_MACOS)
		Locker locker{isolate};
		#endif

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Value> result;
		Local<Value> argv[1];
		KromCallbackdata *cbd = (KromCallbackdata *)callbackdata;
		if (body != NULL) {
			std::unique_ptr<v8::BackingStore> backing = v8::ArrayBuffer::NewBackingStore((void *)body, cbd->size > 0 ? cbd->size : strlen(body), [](void *, size_t, void *) {}, nullptr);
			argv[0] = ArrayBuffer::New(isolate, std::move(backing));
		}
		Local<Function> func = Local<Function>::New(isolate, cbd->func);
		if (!func->Call(context, context->Global(), body != NULL ? 1 : 0, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
		delete cbd;
	}

	void krom_http_request(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value url(isolate, args[0]);

		KromCallbackdata *cbd = new KromCallbackdata();
		cbd->size = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		Local<Function> func = Local<Function>::Cast(args[2]);
		cbd->func.Reset(isolate, func);

		char url_base[512];
		char url_path[512];
		const char *curl = *url;
		int i = 0;
		for (; i < strlen(curl) - 8; ++i) {
			if (curl[i + 8] == '/') break;
			url_base[i] = curl[i + 8]; // Strip https://
		}
		url_base[i] = 0;
		int j = 0;
		if (strlen(url_base) < strlen(curl) - 8) ++i; // Skip /
		for (; j < strlen(curl) - 8 - i; ++j) {
			if (curl[i + 8 + j] == 0) break;
			url_path[j] = curl[i + 8 + j];
		}
		url_path[j] = 0;
		kinc_http_request(url_base, url_path, NULL, 443, true, 0, NULL, &krom_http_callback, cbd);
	}

	#ifdef WITH_COMPUTE
	void krom_set_bool_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();
		int32_t value = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_compute_set_bool(*location, value != 0);
	}

	void krom_set_int_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();
		int32_t value = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_compute_set_int(*location, value);
	}

	void krom_set_float_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();
		float value = (float)args[1]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_compute_set_float(*location, value);
	}

	void krom_set_float2_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();
		float value1 = (float)args[1]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value2 = (float)args[2]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_compute_set_float2(*location, value1, value2);
	}

	void krom_set_float3_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();
		float value1 = (float)args[1]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value2 = (float)args[2]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value3 = (float)args[3]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_compute_set_float3(*location, value1, value2, value3);
	}

	void krom_set_float4_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();
		float value1 = (float)args[1]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value2 = (float)args[2]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value3 = (float)args[3]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		float value4 = (float)args[4]->ToNumber(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_compute_set_float4(*location, value1, value2, value3, value4);
	}

	void krom_set_floats_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();

		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		float *from = (float *)content->Data();
		kinc_compute_set_floats(*location, from, int(content->ByteLength() / 4));
	}

	void krom_set_matrix_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		float *from = (float *)content->Data();
		kinc_compute_set_matrix4(*location, (kinc_matrix4x4_t *)from);
	}

	void krom_set_matrix3_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> locationfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_constant_location_t *location = (kinc_compute_constant_location_t *)locationfield->Value();
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[1]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		float *from = (float *)content->Data();
		kinc_compute_set_matrix3(*location, (kinc_matrix3x3_t *)from);
	}

	void krom_set_texture_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_texture_unit_t *unit = (kinc_compute_texture_unit_t *)unitfield->Value();
		Local<External> texfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)texfield->Value();
		int access = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		kinc_compute_set_texture(*unit, texture, (kinc_compute_access_t)access);
	}

	void krom_set_render_target_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_texture_unit_t *unit = (kinc_compute_texture_unit_t *)unitfield->Value();
		Local<External> rtfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)rtfield->Value();
		int access = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust();
		kinc_compute_set_render_target(*unit, render_target, (kinc_compute_access_t)access);
	}

	void krom_set_sampled_texture_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_texture_unit_t *unit = (kinc_compute_texture_unit_t *)unitfield->Value();
		Local<External> texfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_texture_t *texture = (kinc_g4_texture_t *)texfield->Value();
		kinc_compute_set_sampled_texture(*unit, texture);
	}

	void krom_set_sampled_render_target_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_texture_unit_t *unit = (kinc_compute_texture_unit_t *)unitfield->Value();
		Local<External> rtfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)rtfield->Value();
		kinc_compute_set_sampled_render_target(*unit, render_target);
	}

	void krom_set_sampled_depth_texture_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_texture_unit_t *unit = (kinc_compute_texture_unit_t *)unitfield->Value();
		Local<External> rtfield = Local<External>::Cast(args[1]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_g4_render_target_t *render_target = (kinc_g4_render_target_t *)rtfield->Value();
		kinc_compute_set_sampled_depth_from_render_target(*unit, render_target);
	}

	void krom_set_texture_parameters_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_texture_unit_t *unit = (kinc_compute_texture_unit_t *)unitfield->Value();
		kinc_compute_set_texture_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_U, (kinc_g4_texture_addressing_t)args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_V, (kinc_g4_texture_addressing_t)args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture_minification_filter(*unit, (kinc_g4_texture_filter_t)args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture_magnification_filter(*unit, (kinc_g4_texture_filter_t)args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture_mipmap_filter(*unit, (kinc_g4_mipmap_filter_t)args[5]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
	}

	void krom_set_texture3d_parameters_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> unitfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_texture_unit_t *unit = (kinc_compute_texture_unit_t *)unitfield->Value();
		kinc_compute_set_texture3d_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_U, (kinc_g4_texture_addressing_t)args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture3d_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_V, (kinc_g4_texture_addressing_t)args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture3d_addressing(*unit, KINC_G4_TEXTURE_DIRECTION_W, (kinc_g4_texture_addressing_t)args[3]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture3d_minification_filter(*unit, (kinc_g4_texture_filter_t)args[4]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture3d_magnification_filter(*unit, (kinc_g4_texture_filter_t)args[5]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
		kinc_compute_set_texture3d_mipmap_filter(*unit, (kinc_g4_mipmap_filter_t)args[6]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Int32Value(isolate->GetCurrentContext()).FromJust());
	}

	void krom_set_shader_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> shaderfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_shader *shader = (kinc_compute_shader *)shaderfield->Value();
		kinc_compute_set_shader(shader);
	}

	void krom_create_shader_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<ArrayBuffer> buffer = Local<ArrayBuffer>::Cast(args[0]);
		std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
		kinc_compute_shader *shader = (kinc_compute_shader *)malloc(sizeof(kinc_compute_shader));
		kinc_compute_shader_init(shader, content->Data(), (int)content->ByteLength());

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		obj->SetInternalField(0, External::New(isolate, shader));
		args.GetReturnValue().Set(obj);
	}

	void krom_delete_shader_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Object> shaderobj = args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked();
		Local<External> shaderfield = Local<External>::Cast(shaderobj->GetInternalField(0));
		kinc_compute_shader *shader = (kinc_compute_shader *)shaderfield->Value();
		kinc_compute_shader_destroy(shader);
		free(shader);
	}

	void krom_get_constant_location_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> shaderfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_shader *shader = (kinc_compute_shader *)shaderfield->Value();

		String::Utf8Value utf8_value(isolate, args[1]);
		kinc_compute_constant_location_t location = kinc_compute_shader_get_constant_location(shader, *utf8_value);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		kinc_compute_constant_location_t *location_copy = (kinc_compute_constant_location_t *)malloc(sizeof(kinc_compute_constant_location_t)); // TODO
		memcpy(location_copy, &location, sizeof(kinc_compute_constant_location_t));
		obj->SetInternalField(0, External::New(isolate, location_copy));
		args.GetReturnValue().Set(obj);
	}

	void krom_get_texture_unit_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<External> shaderfield = Local<External>::Cast(args[0]->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->GetInternalField(0));
		kinc_compute_shader *shader = (kinc_compute_shader *)shaderfield->Value();

		String::Utf8Value utf8_value(isolate, args[1]);
		kinc_compute_texture_unit_t unit = kinc_compute_shader_get_texture_unit(shader, *utf8_value);

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);

		Local<Object> obj = templ->NewInstance(isolate->GetCurrentContext()).ToLocalChecked();
		kinc_compute_texture_unit_t *unit_copy = (kinc_compute_texture_unit_t *)malloc(sizeof(kinc_compute_texture_unit_t)); // TODO
		memcpy(unit_copy, &unit, sizeof(kinc_compute_texture_unit_t));
		obj->SetInternalField(0, External::New(isolate, unit_copy));
		args.GetReturnValue().Set(obj);
	}

	void krom_compute(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int x = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int y = args[1]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		int z = args[2]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_compute(x, y, z);
	}
	#endif

	bool window_close_callback(void *data) {
		return true;
	}

	void krom_set_save_and_quit_callback(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		Local<Value> arg = args[0];
		Local<Function> func = Local<Function>::Cast(arg);
		save_and_quit_func.Reset(isolate, func);
		save_and_quit_func_set = true;
		kinc_window_set_close_callback(0, window_close_callback, NULL);
	}

	void krom_set_mouse_cursor(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int id = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		kinc_mouse_set_cursor(id);
		#ifdef KORE_WINDOWS
		// Set hand icon for drag even when mouse button is pressed
		if (id == 1) SetCursor(LoadCursor(NULL, IDC_HAND));
		#endif
	}

	void krom_delay_idle_sleep_fast(Local<Object> receiver) {
		paused_frames = 0;
	}

	void krom_delay_idle_sleep(const FunctionCallbackInfo<Value> &args) {
		krom_delay_idle_sleep_fast(args.This());
	}

	void krom_file_exists(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		bool exists = false;
		String::Utf8Value utf8_value(isolate, args[0]);

		kinc_file_reader_t reader;
		if (kinc_file_reader_open(&reader, *utf8_value, KINC_FILE_TYPE_ASSET)) {
			exists = true;
			kinc_file_reader_close(&reader);
		}

		args.GetReturnValue().Set(Int32::New(isolate, exists));
	}

	void krom_delete_file(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		String::Utf8Value utf8_value(isolate, args[0]);
		#if defined(KORE_WINDOWS)
		char path[1024];
		strcpy(path, "del /f \"");
		strcat(path, *utf8_value);
		strcat(path, "\"");
		sys_command(path);
		#else
		char path[1024];
		strcpy(path, "rm \"");
		strcat(path, *utf8_value);
		strcat(path, "\"");
		sys_command(path);
		#endif
	}

	void krom_window_x(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, kinc_window_x(windowId)));
	}

	void krom_window_y(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		int windowId = args[0]->ToInt32(isolate->GetCurrentContext()).ToLocalChecked()->Value();
		args.GetReturnValue().Set(Int32::New(isolate, kinc_window_y(windowId)));
	}

	void krom_language(const FunctionCallbackInfo<Value> &args) {
		HandleScope scope(args.GetIsolate());
		args.GetReturnValue().Set(String::NewFromUtf8(isolate, kinc_language()).ToLocalChecked());
	}

	#define SET_FUNCTION_FAST(object, name, fn)\
		CFunction fn ## _ = CFunction::Make(fn ## _fast);\
		object->Set(String::NewFromUtf8(isolate, name).ToLocalChecked(),\
		FunctionTemplate::New(isolate, fn, Local<v8::Value>(), Local<v8::Signature>(), 0,\
		v8::ConstructorBehavior::kThrow, v8::SideEffectType::kHasNoSideEffect, &fn ## _))

	#define SET_FUNCTION(object, name, fn)\
		object->Set(String::NewFromUtf8(isolate, name).ToLocalChecked(),\
		FunctionTemplate::New(isolate, fn, Local<v8::Value>(), Local<v8::Signature>(), 0,\
		v8::ConstructorBehavior::kThrow, v8::SideEffectType::kHasNoSideEffect, nullptr))

	void start_v8(char *krom_bin, int krom_bin_size) {
		plat = platform::NewDefaultPlatform();
		V8::InitializePlatform(plat.get());

		std::string flags = "";
		V8::SetFlagsFromString(flags.c_str(), (int)flags.size());

		V8::Initialize();

		Isolate::CreateParams create_params;
		create_params.array_buffer_allocator = ArrayBuffer::Allocator::NewDefaultAllocator();
		StartupData blob;
		if (krom_bin_size > 0) {
			blob.data = krom_bin;
			blob.raw_size = krom_bin_size;
			create_params.snapshot_blob = &blob;
		}
		isolate = Isolate::New(create_params);

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);

		Local<ObjectTemplate> krom = ObjectTemplate::New(isolate);
		SET_FUNCTION(krom, "init", krom_init);
		SET_FUNCTION(krom, "setApplicationName", krom_set_application_name);
		SET_FUNCTION(krom, "log", krom_log);
		SET_FUNCTION_FAST(krom, "clear", krom_clear);
		SET_FUNCTION(krom, "setCallback", krom_set_callback);
		SET_FUNCTION(krom, "setDropFilesCallback", krom_set_drop_files_callback);
		SET_FUNCTION(krom, "setCutCopyPasteCallback", krom_set_cut_copy_paste_callback); ////
		SET_FUNCTION(krom, "setApplicationStateCallback", krom_set_application_state_callback);
		SET_FUNCTION(krom, "setKeyboardDownCallback", krom_set_keyboard_down_callback);
		SET_FUNCTION(krom, "setKeyboardUpCallback", krom_set_keyboard_up_callback);
		SET_FUNCTION(krom, "setKeyboardPressCallback", krom_set_keyboard_press_callback);
		SET_FUNCTION(krom, "setMouseDownCallback", krom_set_mouse_down_callback);
		SET_FUNCTION(krom, "setMouseUpCallback", krom_set_mouse_up_callback);
		SET_FUNCTION(krom, "setMouseMoveCallback", krom_set_mouse_move_callback);
		SET_FUNCTION(krom, "setTouchDownCallback", krom_set_touch_down_callback);
		SET_FUNCTION(krom, "setTouchUpCallback", krom_set_touch_up_callback);
		SET_FUNCTION(krom, "setTouchMoveCallback", krom_set_touch_move_callback);
		SET_FUNCTION(krom, "setMouseWheelCallback", krom_set_mouse_wheel_callback);
		SET_FUNCTION(krom, "setPenDownCallback", krom_set_pen_down_callback);
		SET_FUNCTION(krom, "setPenUpCallback", krom_set_pen_up_callback);
		SET_FUNCTION(krom, "setPenMoveCallback", krom_set_pen_move_callback);
		SET_FUNCTION(krom, "setGamepadAxisCallback", krom_set_gamepad_axis_callback);
		SET_FUNCTION(krom, "setGamepadButtonCallback", krom_set_gamepad_button_callback);
		SET_FUNCTION_FAST(krom, "lockMouse", krom_lock_mouse);
		SET_FUNCTION_FAST(krom, "unlockMouse", krom_unlock_mouse);
		SET_FUNCTION_FAST(krom, "canLockMouse", krom_can_lock_mouse);
		SET_FUNCTION_FAST(krom, "isMouseLocked", krom_is_mouse_locked);
		SET_FUNCTION_FAST(krom, "setMousePosition", krom_set_mouse_position);
		SET_FUNCTION_FAST(krom, "showMouse", krom_show_mouse);
		SET_FUNCTION_FAST(krom, "showKeyboard", krom_show_keyboard);
		SET_FUNCTION(krom, "createIndexBuffer", krom_create_indexbuffer);
		SET_FUNCTION(krom, "deleteIndexBuffer", krom_delete_indexbuffer);
		SET_FUNCTION(krom, "lockIndexBuffer", krom_lock_indexbuffer);
		SET_FUNCTION(krom, "unlockIndexBuffer", krom_unlock_indexbuffer);
		SET_FUNCTION(krom, "setIndexBuffer", krom_set_indexbuffer);
		SET_FUNCTION(krom, "createVertexBuffer", krom_create_vertexbuffer);
		SET_FUNCTION(krom, "deleteVertexBuffer", krom_delete_vertexbuffer);
		SET_FUNCTION(krom, "lockVertexBuffer", krom_lock_vertex_buffer);
		SET_FUNCTION(krom, "unlockVertexBuffer", krom_unlock_vertex_buffer);
		SET_FUNCTION(krom, "setVertexBuffer", krom_set_vertexbuffer);
		SET_FUNCTION(krom, "setVertexBuffers", krom_set_vertexbuffers);
		SET_FUNCTION_FAST(krom, "drawIndexedVertices", krom_draw_indexed_vertices);
		SET_FUNCTION_FAST(krom, "drawIndexedVerticesInstanced", krom_draw_indexed_vertices_instanced);
		SET_FUNCTION(krom, "createVertexShader", krom_create_vertex_shader);
		SET_FUNCTION(krom, "createVertexShaderFromSource", krom_create_vertex_shader_from_source);
		SET_FUNCTION(krom, "createFragmentShader", krom_create_fragment_shader);
		SET_FUNCTION(krom, "createFragmentShaderFromSource", krom_create_fragment_shader_from_source);
		SET_FUNCTION(krom, "createGeometryShader", krom_create_geometry_shader);
		SET_FUNCTION(krom, "createTessellationControlShader", krom_create_tessellation_control_shader);
		SET_FUNCTION(krom, "createTessellationEvaluationShader", krom_create_tessellation_evaluation_shader);
		SET_FUNCTION(krom, "deleteShader", krom_delete_shader);
		SET_FUNCTION(krom, "createPipeline", krom_create_pipeline);
		SET_FUNCTION(krom, "deletePipeline", krom_delete_pipeline);
		SET_FUNCTION(krom, "compilePipeline", krom_compile_pipeline);
		SET_FUNCTION(krom, "setPipeline", krom_set_pipeline);
		SET_FUNCTION(krom, "loadImage", krom_load_image);
		SET_FUNCTION(krom, "unloadImage", krom_unload_image);
		// #ifdef WITH_AUDIO
		SET_FUNCTION(krom, "loadSound", krom_load_sound);
		SET_FUNCTION(krom, "setAudioCallback", krom_set_audio_callback);
		SET_FUNCTION(krom, "audioThread", krom_audio_thread);
		SET_FUNCTION(krom, "writeAudioBuffer", krom_write_audio_buffer);
		SET_FUNCTION(krom, "getSamplesPerSecond", krom_get_samples_per_second);
		// #endif
		SET_FUNCTION(krom, "loadBlob", krom_load_blob);
		SET_FUNCTION(krom, "loadUrl", krom_load_url);
		SET_FUNCTION(krom, "copyToClipboard", krom_copy_to_clipboard);
		SET_FUNCTION(krom, "getConstantLocation", krom_get_constant_location);
		SET_FUNCTION(krom, "getTextureUnit", krom_get_texture_unit);
		SET_FUNCTION(krom, "setTexture", krom_set_texture);
		SET_FUNCTION(krom, "setRenderTarget", krom_set_render_target);
		SET_FUNCTION(krom, "setTextureDepth", krom_set_texture_depth);
		SET_FUNCTION(krom, "setImageTexture", krom_set_image_texture);
		SET_FUNCTION(krom, "setTextureParameters", krom_set_texture_parameters);
		SET_FUNCTION(krom, "setTexture3DParameters", krom_set_texture3d_parameters);
		SET_FUNCTION(krom, "setTextureCompareMode", krom_set_texture_compare_mode);
		SET_FUNCTION(krom, "setCubeMapCompareMode", krom_set_cube_map_compare_mode);
		SET_FUNCTION(krom, "setBool", krom_set_bool);
		SET_FUNCTION(krom, "setInt", krom_set_int);
		SET_FUNCTION(krom, "setFloat", krom_set_float);
		SET_FUNCTION(krom, "setFloat2", krom_set_float2);
		SET_FUNCTION(krom, "setFloat3", krom_set_float3);
		SET_FUNCTION(krom, "setFloat4", krom_set_float4);
		SET_FUNCTION(krom, "setFloats", krom_set_floats);
		SET_FUNCTION(krom, "setMatrix", krom_set_matrix);
		SET_FUNCTION(krom, "setMatrix3", krom_set_matrix3);
		SET_FUNCTION_FAST(krom, "getTime", krom_get_time);
		SET_FUNCTION_FAST(krom, "windowWidth", krom_window_width);
		SET_FUNCTION_FAST(krom, "windowHeight", krom_window_height);
		SET_FUNCTION(krom, "setWindowTitle", krom_set_window_title);
		SET_FUNCTION(krom, "getWindowMode", krom_get_window_mode);
		SET_FUNCTION(krom, "setWindowMode", krom_set_window_mode);
		SET_FUNCTION(krom, "resizeWindow", krom_resize_window);
		SET_FUNCTION(krom, "moveWindow", krom_move_window);
		SET_FUNCTION(krom, "screenDpi", krom_screen_dpi);
		SET_FUNCTION(krom, "systemId", krom_system_id);
		SET_FUNCTION(krom, "requestShutdown", krom_request_shutdown);
		SET_FUNCTION(krom, "displayCount", krom_display_count);
		SET_FUNCTION(krom, "displayWidth", krom_display_width);
		SET_FUNCTION(krom, "displayHeight", krom_display_height);
		SET_FUNCTION(krom, "displayX", krom_display_x);
		SET_FUNCTION(krom, "displayY", krom_display_y);
		SET_FUNCTION(krom, "displayFrequency", krom_display_frequency);
		SET_FUNCTION(krom, "displayIsPrimary", krom_display_is_primary);
		SET_FUNCTION(krom, "writeStorage", krom_write_storage);
		SET_FUNCTION(krom, "readStorage", krom_read_storage);
		SET_FUNCTION(krom, "createRenderTarget", krom_create_render_target);
		SET_FUNCTION(krom, "createRenderTargetCubeMap", krom_create_render_target_cube_map);
		SET_FUNCTION(krom, "createTexture", krom_create_texture);
		SET_FUNCTION(krom, "createTexture3D", krom_create_texture3d);
		SET_FUNCTION(krom, "createTextureFromBytes", krom_create_texture_from_bytes);
		SET_FUNCTION(krom, "createTextureFromBytes3D", krom_create_texture_from_bytes3d);
		SET_FUNCTION(krom, "createTextureFromEncodedBytes", krom_create_texture_from_encoded_bytes);
		SET_FUNCTION(krom, "getTexturePixels", krom_get_texture_pixels);
		SET_FUNCTION(krom, "getRenderTargetPixels", krom_get_render_target_pixels);
		SET_FUNCTION(krom, "lockTexture", krom_lock_texture);
		SET_FUNCTION(krom, "unlockTexture", krom_unlock_texture);
		SET_FUNCTION(krom, "clearTexture", krom_clear_texture);
		SET_FUNCTION(krom, "generateTextureMipmaps", krom_generate_texture_mipmaps);
		SET_FUNCTION(krom, "generateRenderTargetMipmaps", krom_generate_render_target_mipmaps);
		SET_FUNCTION(krom, "setMipmaps", krom_set_mipmaps);
		SET_FUNCTION(krom, "setDepthStencilFrom", krom_set_depth_stencil_from);
		SET_FUNCTION_FAST(krom, "viewport", krom_viewport);
		SET_FUNCTION_FAST(krom, "scissor", krom_scissor);
		SET_FUNCTION_FAST(krom, "disableScissor", krom_disable_scissor);
		SET_FUNCTION_FAST(krom, "renderTargetsInvertedY", krom_render_targets_inverted_y);
		SET_FUNCTION(krom, "begin", krom_begin);
		SET_FUNCTION(krom, "beginFace", krom_begin_face);
		SET_FUNCTION(krom, "end", krom_end);
		SET_FUNCTION(krom, "fileSaveBytes", krom_file_save_bytes);
		SET_FUNCTION(krom, "sysCommand", krom_sys_command);
		SET_FUNCTION(krom, "savePath", krom_save_path);
		SET_FUNCTION(krom, "getArgCount", krom_get_arg_count);
		SET_FUNCTION(krom, "getArg", krom_get_arg);
		SET_FUNCTION(krom, "getFilesLocation", krom_get_files_location);
		SET_FUNCTION(krom, "httpRequest", krom_http_request);
		#ifdef WITH_COMPUTE
		SET_FUNCTION(krom, "setBoolCompute", krom_set_bool_compute);
		SET_FUNCTION(krom, "setIntCompute", krom_set_int_compute);
		SET_FUNCTION(krom, "setFloatCompute", krom_set_float_compute);
		SET_FUNCTION(krom, "setFloat2Compute", krom_set_float2_compute);
		SET_FUNCTION(krom, "setFloat3Compute", krom_set_float3_compute);
		SET_FUNCTION(krom, "setFloat4Compute", krom_set_float4_compute);
		SET_FUNCTION(krom, "setFloatsCompute", krom_set_floats_compute);
		SET_FUNCTION(krom, "setMatrixCompute", krom_set_matrix_compute);
		SET_FUNCTION(krom, "setMatrix3Compute", krom_set_matrix3_compute);
		SET_FUNCTION(krom, "setTextureCompute", krom_set_texture_compute);
		SET_FUNCTION(krom, "setRenderTargetCompute", krom_set_render_target_compute);
		SET_FUNCTION(krom, "setSampledTextureCompute", krom_set_sampled_texture_compute);
		SET_FUNCTION(krom, "setSampledRenderTargetCompute", krom_set_sampled_render_target_compute);
		SET_FUNCTION(krom, "setSampledDepthTextureCompute", krom_set_sampled_depth_texture_compute);
		SET_FUNCTION(krom, "setTextureParametersCompute", krom_set_texture_parameters_compute);
		SET_FUNCTION(krom, "setTexture3DParametersCompute", krom_set_texture3d_parameters_compute);
		SET_FUNCTION(krom, "setShaderCompute", krom_set_shader_compute);
		SET_FUNCTION(krom, "deleteShaderCompute", krom_delete_shader_compute);
		SET_FUNCTION(krom, "createShaderCompute", krom_create_shader_compute);
		SET_FUNCTION(krom, "getConstantLocationCompute", krom_get_constant_location_compute);
		SET_FUNCTION(krom, "getTextureUnitCompute", krom_get_texture_unit_compute);
		SET_FUNCTION(krom, "compute", krom_compute);
		#endif
		SET_FUNCTION(krom, "setSaveAndQuitCallback", krom_set_save_and_quit_callback);
		SET_FUNCTION(krom, "setMouseCursor", krom_set_mouse_cursor);
		SET_FUNCTION_FAST(krom, "delayIdleSleep", krom_delay_idle_sleep);
		SET_FUNCTION(krom, "fileExists", krom_file_exists);
		SET_FUNCTION(krom, "deleteFile", krom_delete_file);
		SET_FUNCTION(krom, "windowX", krom_window_x);
		SET_FUNCTION(krom, "windowY", krom_window_y);
		SET_FUNCTION(krom, "language", krom_language);

		Local<ObjectTemplate> global = ObjectTemplate::New(isolate);
		global->Set(String::NewFromUtf8(isolate, "Krom").ToLocalChecked(), krom);

		Local<Context> context = Context::New(isolate, NULL, global);
		global_context.Reset(isolate, context);
	}

	void start_krom(char *scriptfile) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		if (scriptfile != NULL) {
			Local<String> source = String::NewFromUtf8(isolate, scriptfile, NewStringType::kNormal).ToLocalChecked();

			TryCatch try_catch(isolate);
			Local<Script> compiled_script = Script::Compile(isolate->GetCurrentContext(), source).ToLocalChecked();

			Local<Value> result;
			if (!compiled_script->Run(context).ToLocal(&result)) {
				handle_exception(&try_catch);
			}
		}
		else {
			TryCatch try_catch(isolate);
			Local<Value> js_kickstart = context->Global()->Get(isolate->GetCurrentContext(), String::NewFromUtf8(isolate, "kickstart").ToLocalChecked()).ToLocalChecked();
			if (!js_kickstart->IsNullOrUndefined()) {
				Local<Value> result;
				if (!js_kickstart->ToObject(isolate->GetCurrentContext()).ToLocalChecked()->CallAsFunction(context, context->Global(), 0, nullptr).ToLocal(&result)) {
					handle_exception(&try_catch);
				}
			}
		}
	}

	void update(void *data) {
		#ifdef KORE_WINDOWS
		if (show_window && enable_window) {
			show_window = false;
			kinc_window_show(0);
		}
		#endif

		#ifdef WITH_AUDIO
		if (enable_audio) {
			kinc_a2_update();
		}
		#endif

		{ // FIXME: patch to prevent random crashes
			v8::Locker locker{isolate};
			v8::Isolate::Scope isolate_scope(isolate);
			v8::HandleScope handle_scope(isolate);
			v8::Local<v8::Context> context = v8::Local<v8::Context>::New(isolate, global_context);
			v8::Context::Scope context_scope(context);

		#ifdef WITH_WORKER
		handle_worker_messages(isolate, global_context);
		#endif

			v8::MicrotasksScope microtasks(isolate, v8::MicrotasksScope::kDoNotRunMicrotasks);
			{
				v8::TryCatch tc(isolate);
				v8::Local<v8::Function> func = v8::Local<v8::Function>::New(isolate, update_func);
				v8::Local<v8::Value> result;
				if (!func.IsEmpty()) {
					(void)func->Call(context, context->Global(), 0, nullptr).ToLocal(&result);
				}
				if (tc.HasCaught()) handle_exception(&tc);
			}
			v8::MicrotasksScope::PerformCheckpoint(isolate);
		}

		kinc_g4_begin(0);
		kinc_g4_end(0);
		kinc_g4_swap_buffers();
	}

	void drop_files(wchar_t *file_path, void *data) {
		// Update mouse position
		#ifdef KORE_WINDOWS
		POINT p;
		GetCursorPos(&p);
		ScreenToClient(kinc_windows_window_handle(0), &p);
		mouse_move(0, p.x, p.y, 0, 0, NULL);
		#endif

		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, drop_files_func);
		Local<Value> result;
		const int argc = 1;
		Local<Value> argv[argc];
		if (sizeof(wchar_t) == 2) {
			argv[0] = {String::NewFromTwoByte(isolate, (const uint16_t *)file_path).ToLocalChecked()};
		}
		else {
			size_t len = wcslen(file_path);
			uint16_t *str = new uint16_t[len + 1];
			for (int i = 0; i < len; i++) str[i] = file_path[i];
			str[len] = 0;
			argv[0] = {String::NewFromTwoByte(isolate, str).ToLocalChecked()};
			delete[] str;
		}
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}

		in_background = false;
	}

	char *copy(void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, copy_func);
		Local<Value> result;
		if (!func->Call(context, context->Global(), 0, NULL).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
		String::Utf8Value cutCopyString(isolate, result);
		strcpy(temp_string, *cutCopyString);

		return temp_string;
	}

	char *cut(void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, cut_func);
		Local<Value> result;
		if (!func->Call(context, context->Global(), 0, NULL).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
		String::Utf8Value cutCopyString(isolate, result);
		strcpy(temp_string, *cutCopyString);

		return temp_string;
	}

	void paste(char *text, void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, paste_func);
		Local<Value> result;
		const int argc = 1;
		Local<Value> argv[argc] = {String::NewFromUtf8(isolate, text).ToLocalChecked()};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void foreground(void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, foreground_func);
		Local<Value> result;
		if (!func->Call(context, context->Global(), 0, NULL).ToLocal(&result)) {
			handle_exception(&try_catch);
		}

		in_background = false;
	}

	void resume(void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, resume_func);
		Local<Value> result;
		if (!func->Call(context, context->Global(), 0, NULL).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void pause(void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, pause_func);
		Local<Value> result;
		if (!func->Call(context, context->Global(), 0, NULL).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void background(void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, background_func);
		Local<Value> result;
		if (!func->Call(context, context->Global(), 0, NULL).ToLocal(&result)) {
			handle_exception(&try_catch);
		}

		in_background = true;
		paused_frames = 0;
	}

	void shutdown(void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, shutdown_func);
		Local<Value> result;
		if (!func->Call(context, context->Global(), 0, NULL).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void key_down(int code, void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, keyboard_down_func);
		Local<Value> result;
		const int argc = 1;
		Local<Value> argv[argc] = {Int32::New(isolate, code)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void key_up(int code, void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, keyboard_up_func);
		Local<Value> result;
		const int argc = 1;
		Local<Value> argv[argc] = {Int32::New(isolate, code)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void key_press(unsigned int character, void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, keyboard_press_func);
		Local<Value> result;
		const int argc = 1;
		Local<Value> argv[argc] = {Int32::New(isolate, character)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void mouse_move(int window, int x, int y, int mx, int my, void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, mouse_move_func);
		Local<Value> result;
		const int argc = 4;
		Local<Value> argv[argc] = {Int32::New(isolate, x), Int32::New(isolate, y), Int32::New(isolate, mx), Int32::New(isolate, my)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void mouse_down(int window, int button, int x, int y, void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, mouse_down_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, button), Int32::New(isolate, x), Int32::New(isolate, y)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void mouse_up(int window, int button, int x, int y, void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, mouse_up_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, button), Int32::New(isolate, x), Int32::New(isolate, y)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void mouse_wheel(int window, int delta, void *data) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, mouse_wheel_func);
		Local<Value> result;
		const int argc = 1;
		Local<Value> argv[argc] = {Int32::New(isolate, delta)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void touch_move(int index, int x, int y) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, touch_move_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, index), Int32::New(isolate, x), Int32::New(isolate, y)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void touch_down(int index, int x, int y) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, touch_down_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, index), Int32::New(isolate, x), Int32::New(isolate, y)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void touch_up(int index, int x, int y) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, touch_up_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, index), Int32::New(isolate, x), Int32::New(isolate, y)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void pen_down(int window, int x, int y, float pressure) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, pen_down_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, x), Int32::New(isolate, y), Number::New(isolate, pressure)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void pen_up(int window, int x, int y, float pressure) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, pen_up_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, x), Int32::New(isolate, y), Number::New(isolate, pressure)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void pen_move(int window, int x, int y, float pressure) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, pen_move_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, x), Int32::New(isolate, y), Number::New(isolate, pressure)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void gamepad_axis(int gamepad, int axis, float value) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, gamepad_axis_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, gamepad), Int32::New(isolate, axis), Number::New(isolate, value)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}

	void gamepad_button(int gamepad, int button, float value) {
		Locker locker{isolate};

		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);
		Local<Context> context = Local<Context>::New(isolate, global_context);
		Context::Scope context_scope(context);

		TryCatch try_catch(isolate);
		Local<Function> func = Local<Function>::New(isolate, gamepad_button_func);
		Local<Value> result;
		const int argc = 3;
		Local<Value> argv[argc] = {Int32::New(isolate, gamepad), Int32::New(isolate, button), Number::New(isolate, value)};
		if (!func->Call(context, context->Global(), argc, argv).ToLocal(&result)) {
			handle_exception(&try_catch);
		}
	}
}

int kickstart(int argc, char **argv) {
	_argc = argc;
	_argv = argv;
	std::string bindir(argv[0]);

#ifdef KORE_WINDOWS // Handle non-ascii path
	HMODULE hModule = GetModuleHandleW(NULL);
	GetModuleFileNameW(hModule, temp_wstring, 1024);
	WideCharToMultiByte(CP_UTF8, 0, temp_wstring, -1, temp_string, 4096, nullptr, nullptr);
	bindir = temp_string;
#endif

#ifdef KORE_WINDOWS
	bindir = bindir.substr(0, bindir.find_last_of("\\"));
#else
	bindir = bindir.substr(0, bindir.find_last_of("/"));
#endif
	assetsdir = argc > 1 ? argv[1] : bindir;

	// Opening a file
	int l = (int)assetsdir.length();
	if ((l > 6 && assetsdir[l - 6] == '.') ||
		(l > 5 && assetsdir[l - 5] == '.') ||
		(l > 4 && assetsdir[l - 4] == '.')) {
		assetsdir = bindir;
	}

	bool read_console_pid = false;
	for (int i = 2; i < argc; ++i) {
		if (strcmp(argv[i], "--nowindow") == 0) {
			enable_window = false;
		}
		#ifdef WITH_AUDIO
		else if (strcmp(argv[i], "--nosound") == 0) {
			enable_audio = false;
		}
		#endif
		else if (strcmp(argv[i], "--snapshot") == 0) {
			snapshot = true;
		}
		else if (read_console_pid) {
			#ifdef KORE_WINDOWS
			AttachConsole(atoi(argv[i]));
			#endif
			read_console_pid = false;
		}
		else if (strcmp(argv[i], "--consolepid") == 0) {
			read_console_pid = true;
		}
	}

#if !defined(KORE_MACOS)
	kinc_internal_set_files_location(&assetsdir[0u]);
#endif

#ifdef KORE_MACOS
	// Handle loading assets located outside of '.app/Contents/Resources/Deployment' folder
	// when assets and shaders dir is passed as an argument
	if (argc > 2) {
		kinc_internal_set_files_location(&assetsdir[0u]);
	}
#endif

	bool snapshot_found = true;
	kinc_file_reader_t reader;
	if (snapshot || !kinc_file_reader_open(&reader, "krom.bin", KINC_FILE_TYPE_ASSET)) {
		if (!kinc_file_reader_open(&reader, "krom.js", KINC_FILE_TYPE_ASSET)) {
			kinc_log(KINC_LOG_LEVEL_ERROR, "Could not load krom.js, aborting.");
			exit(1);
		}
		snapshot_found = false;
	}

	int reader_size = (int)kinc_file_reader_size(&reader);
	char *code = (char *)malloc(reader_size + 1);
	kinc_file_reader_read(&reader, code, reader_size);
	code[reader_size] = 0;
	kinc_file_reader_close(&reader);

	if (snapshot) {
		plat = platform::NewDefaultPlatform();
		V8::InitializePlatform(plat.get());

		std::string flags = "--nolazy";
		V8::SetFlagsFromString(flags.c_str(), (int)flags.size());
		V8::Initialize();

		ScriptCompiler::CachedData *cache;
		Isolate::CreateParams create_params;
		create_params.array_buffer_allocator = ArrayBuffer::Allocator::NewDefaultAllocator();
		Isolate *isolate_cache = Isolate::New(create_params);
		{
			HandleScope handle_scope(isolate_cache);
			{
				Local<Context> context = Context::New(isolate_cache);
				Context::Scope context_scope(context);

				ScriptOrigin origin(isolate_cache, String::NewFromUtf8(isolate_cache, "krom_cache").ToLocalChecked());
				ScriptCompiler::Source source(String::NewFromUtf8(isolate_cache, code).ToLocalChecked(), origin);

				Local<Script> compiled_script = ScriptCompiler::Compile(context, &source, ScriptCompiler::kEagerCompile).ToLocalChecked();
				cache = ScriptCompiler::CreateCodeCache(compiled_script->GetUnboundScript());
			}
		}

		SnapshotCreator creator_cold;
		Isolate *isolate_cold = creator_cold.GetIsolate();
		{
			HandleScope handle_scope(isolate_cold);
			{
				Local<Context> context = Context::New(isolate_cold);
				Context::Scope context_scope(context);

				const size_t line_size = 512;
				char line[line_size];
				strcpy(line, assetsdir.c_str());
				strcat(line, "/data/embed.txt");
				FILE *fp = fopen (line, "r");
				if (fp != NULL) {
					while (fgets(line, line_size, fp) != NULL)  {
						line[strlen(line) - 1] = 0; // Trim \n
						kinc_file_reader_t reader;
						if (!kinc_file_reader_open(&reader, line, KINC_FILE_TYPE_ASSET)) continue;
						int reader_size = (int)kinc_file_reader_size(&reader);

						Local<ArrayBuffer> buffer = ArrayBuffer::New(isolate_cold, reader_size);
						std::shared_ptr<BackingStore> content = buffer->GetBackingStore();
						kinc_file_reader_read(&reader, content->Data(), reader_size);
						kinc_file_reader_close(&reader);

						(void) context->Global()->Set(context, String::NewFromUtf8(isolate_cold, line).ToLocalChecked(), buffer);
					}
					fclose (fp);
				}

				ScriptOrigin origin(isolate_cache, String::NewFromUtf8(isolate_cold, "krom_cold").ToLocalChecked());
				ScriptCompiler::Source source(String::NewFromUtf8(isolate_cold, code).ToLocalChecked(), origin, cache);

				Local<Script> compiled_script = ScriptCompiler::Compile(context, &source, ScriptCompiler::kConsumeCodeCache).ToLocalChecked();
				(void) compiled_script->Run(context);

				creator_cold.SetDefaultContext(context);
			}
		}
		StartupData coldData = creator_cold.CreateBlob(SnapshotCreator::FunctionCodeHandling::kKeep);

		// SnapshotCreator creator_warm(nullptr, &coldData);
		// Isolate *isolate_warm = creator_warm.GetIsolate();
		// {
		// 	HandleScope handle_scope(isolate_warm);
		// 	{
		// 		Local<Context> context = Context::New(isolate_warm);
		// 		Context::Scope context_scope(context);

		// 		// std::string code_warm("Main.main();");
		// 		ScriptOrigin origin(String::NewFromUtf8(isolate_warm, "krom_warm").ToLocalChecked());
		// 		ScriptCompiler::Source source(String::NewFromUtf8(isolate_warm, code).ToLocalChecked(), origin);

		// 		Local<Script> compiled_script = ScriptCompiler::Compile(context, &source, ScriptCompiler::kEagerCompile).ToLocalChecked();
		// 		compiled_script->Run(context);
		// 	}
		// }
		// {
		//   HandleScope handle_scope(isolate_warm);
		//   isolate_warm->ContextDisposedNotification(false);
		//   Local<Context> context = Context::New(isolate_warm);
		//   creator_warm.SetDefaultContext(context);
		// }
		// StartupData warmData = creator_warm.CreateBlob(SnapshotCreator::FunctionCodeHandling::kKeep);

		std::string krombin = assetsdir + "/krom.bin";
		FILE *file = fopen(&krombin[0u], "wb");
		if (file != nullptr) {
			// fwrite(warmData.data, 1, warmData.raw_size, file);
			fwrite(coldData.data, 1, coldData.raw_size, file);
			fclose(file);
		}
		exit(0);
	}

	kinc_threads_init();
	kinc_display_init();

	start_v8(snapshot_found ? code : NULL, snapshot_found ? reader_size : 0);
	#ifdef WITH_WORKER
	bind_worker_class(isolate, global_context);
	#endif
	start_krom(snapshot_found ? NULL : code);

	kinc_start();

	#ifdef WITH_AUDIO
	if (enable_audio) {
		kinc_a2_shutdown();
	}
	#endif

	free(code);

	return 0;
}
