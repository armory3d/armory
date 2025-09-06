#include "worker.h"

#include <vector>

#include <stdlib.h>
#include <string.h>

#include <kinc/log.h>
#include <kinc/threads/thread.h>
#include <kinc/threads/mutex.h>
#include <kinc/io/filereader.h>
#include <kinc/system.h>

using namespace v8;

namespace {
	const uint32_t worker_data_slot = 0;

	struct WorkerMessage {
		char* message;
		int length;
	};

	struct MessageQueue {
		std::vector<WorkerMessage> messages;
		kinc_mutex_t messageMutex;
		Global<Function> messageFunc;
	};

	struct WorkerMessagePort {
		MessageQueue workerMessages;
		MessageQueue ownerMessages;

		bool isTerminated = false;
	};

	struct WorkerData {
		char fileName[256];
		WorkerMessagePort* messagePort;
	};

	struct OwnedWorker {
		kinc_thread_t* workerThread;
		WorkerMessagePort* workerMessagePort;
	};

	struct ContextData {
		std::vector<OwnedWorker> workers;
	};

	struct IntervalFunction {
		Global<Function> function;
		double interval;
		double nextCallTime;
		int id;
	};

	struct IntervalFunctions {
		std::vector<IntervalFunction> functions;
		int latestId;
	};

	void set_onmessage(MessageQueue* messageQueue, Isolate* isolate, Local<Value> callback) {
		if (callback->IsFunction()) {
			messageQueue->messageFunc.Reset(isolate, Local<Function>::Cast(callback));
		}
		else if (callback->IsNullOrUndefined()) {
			messageQueue->messageFunc.Reset();
		}
		else {
			kinc_log(KINC_LOG_LEVEL_ERROR, "[set_onmessage]: argument is neither a function nor null");
		}
	}

	void post_message(MessageQueue* messageQueue, Isolate* isolate, Local<Value> messageObject) {
		Local<String> result = JSON::Stringify(isolate->GetCurrentContext(), messageObject).ToLocalChecked();

		WorkerMessage message;
		message.length = result->Length();
		message.message = new char[message.length];
		result->WriteUtf8(isolate, message.message, message.length);

		kinc_mutex_lock(&messageQueue->messageMutex);
		messageQueue->messages.push_back(message);
		kinc_mutex_unlock(&messageQueue->messageMutex);
	}

	void handle_message_queue(Isolate* isolate, const Global<Context>& context, MessageQueue* messageQueue) {
		if (messageQueue->messageFunc.IsEmpty()) {
			return;
		}

		HandleScope scope(isolate);
		Local<Context> current_context = Local<Context>::New(isolate, context);
		Context::Scope context_scope(current_context);

		kinc_mutex_lock(&messageQueue->messageMutex);

		for (WorkerMessage& message : messageQueue->messages) {
			MaybeLocal<Value> value = JSON::Parse(current_context, String::NewFromUtf8(isolate, message.message, NewStringType::kNormal, message.length).ToLocalChecked());
			delete[] message.message;
			Local<Object> object = Object::New(isolate);
			object->Set(current_context, String::NewFromUtf8(isolate, "data").ToLocalChecked(), value.ToLocalChecked());
			Local<Value> args[] = { object };

			Local<Function> message_func = messageQueue->messageFunc.Get(isolate);
			message_func->Call(current_context, current_context->Global(), 1, args);
		}

		messageQueue->messages.clear();

		kinc_mutex_unlock(&messageQueue->messageMutex);
	}

	void handle_exception(Isolate* isolate, TryCatch* try_catch) {
		MaybeLocal<Value> trace = try_catch->StackTrace(isolate->GetCurrentContext());
		if (trace.IsEmpty()) {
			v8::String::Utf8Value stack_trace(isolate, try_catch->Message()->Get());
			kinc_log(KINC_LOG_LEVEL_ERROR, "uncaught exception %s", *stack_trace);
		}
		else {
			v8::String::Utf8Value stack_trace(isolate, trace.ToLocalChecked());
			kinc_log(KINC_LOG_LEVEL_ERROR, "uncaught exception %s", *stack_trace);
		}
	}

	void worker_post_message(const FunctionCallbackInfo<Value>& args) {
		Isolate* isolate = args.GetIsolate();
		HandleScope scope(isolate);
		if (args.Length() < 1) {
			return;
		}
		if (args.Length() > 1) {
			kinc_log(KINC_LOG_LEVEL_WARNING, "Krom workers only support 1 argument for postMessage");
		}

		Local<External> external = Local<External>::Cast(args.Data());
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();
		post_message(&messagePort->workerMessages, isolate, args[0]);
	}

	void worker_onmessage_get(Local<String> property, const PropertyCallbackInfo<Value>& info) {
		Isolate* isolate = info.GetIsolate();
		HandleScope scope(isolate);

		Local<External> external = Local<External>::Cast(info.Data());
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();

		info.GetReturnValue().Set(messagePort->ownerMessages.messageFunc);
	}

	void worker_onmessage_set(Local<String> property, Local<Value> value, const PropertyCallbackInfo<Value>& info) {
		Isolate* isolate = info.GetIsolate();
		HandleScope scope(isolate);

		Local<External> external = Local<External>::Cast(info.Data());
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();

		set_onmessage(&messagePort->ownerMessages, isolate, value);
	}

	void worker_add_event_listener(const FunctionCallbackInfo<Value>& args) {
		Isolate* isolate = args.GetIsolate();
		HandleScope scope(isolate);

		if (args.Length() < 2) {
			return;
		}

		Local<String> name = Local<String>::Cast(args[0]);
		char event_name[256];
		int length = name->WriteUtf8(isolate, event_name, 255);
		event_name[length] = 0;
		if (strcmp(event_name, "message") != 0) {
			kinc_log(KINC_LOG_LEVEL_WARNING, "Trying to add listener for unknown event %s", event_name);
			return;
		}

		Local<External> external = Local<External>::Cast(args.Data());
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();

		set_onmessage(&messagePort->ownerMessages, isolate, args[1]);
	}

	void worker_set_interval(const FunctionCallbackInfo<Value>& args) {
		Isolate* isolate = args.GetIsolate();
		HandleScope scope(isolate);

		Local<External> external = Local<External>::Cast(args.Data());
		IntervalFunctions* interval_functions = (IntervalFunctions*)external->Value();

		Local<Function> function = Local<Function>::Cast(args[0]);

		double frequency;
		if (args.Length() > 1) {
			frequency = Local<Number>::Cast(args[1])->Value();
			frequency /= 1000.0;
		}
		else {
			frequency = 0.016;
		}

		interval_functions->functions.emplace_back();
		IntervalFunction& interval_function = interval_functions->functions[interval_functions->functions.size() - 1];
		interval_function.function.Reset(isolate, function);
		interval_function.interval = frequency;
		interval_function.nextCallTime = kinc_time() + frequency;
		interval_function.id = interval_functions->latestId;

		interval_functions->latestId++;

		args.GetReturnValue().Set(interval_function.id);
	}

	void worker_clear_interval(const FunctionCallbackInfo<Value>& args) {
		Local<External> external = Local<External>::Cast(args.Data());
		IntervalFunctions* intervalFunctions = (IntervalFunctions*)external->Value();

		int id = Local<Int32>::Cast(args[0])->Value();

		for (std::vector<IntervalFunction>::iterator it = intervalFunctions->functions.begin(); it != intervalFunctions->functions.end(); ++it) {
			if (it->id == id) {
				it->function.Reset();
				intervalFunctions->functions.erase(it);
				return;
			}
		}
	}

	void worker_thread_func(void* param) {
		WorkerData* worker_data = (WorkerData*)param;
		WorkerMessagePort* message_port = worker_data->messagePort;

		Isolate::CreateParams create_params;
		create_params.array_buffer_allocator = v8::ArrayBuffer::Allocator::NewDefaultAllocator();
		Isolate* isolate = Isolate::New(create_params);
		Locker locker(isolate);
		Isolate::Scope isolate_scope(isolate);
		HandleScope handle_scope(isolate);

		Local<ObjectTemplate> global = ObjectTemplate::New(isolate);

		Local<External> extern_message_port = External::New(isolate, message_port);
		global->Set(String::NewFromUtf8(isolate, "postMessage").ToLocalChecked(), FunctionTemplate::New(isolate, worker_post_message, extern_message_port));
		global->SetAccessor(String::NewFromUtf8(isolate, "onmessage").ToLocalChecked(), (AccessorGetterCallback)worker_onmessage_get, (AccessorSetterCallback)worker_onmessage_set, extern_message_port);
		global->Set(String::NewFromUtf8(isolate, "addEventListener").ToLocalChecked(), FunctionTemplate::New(isolate, worker_add_event_listener, extern_message_port));

		IntervalFunctions interval_functions;
		interval_functions.latestId = 0;
		Local<External> extern_interval_functions = External::New(isolate, &interval_functions);

		global->Set(String::NewFromUtf8(isolate, "setInterval").ToLocalChecked(), FunctionTemplate::New(isolate, worker_set_interval, extern_interval_functions));
		global->Set(String::NewFromUtf8(isolate, "clearInterval").ToLocalChecked(), FunctionTemplate::New(isolate, worker_clear_interval, extern_interval_functions));

		Local<Context> context = Context::New(isolate, nullptr, global);
		Global<Context> global_context;
		global_context.Reset(isolate, context);
		Context::Scope context_scope(context);

		bind_worker_class(isolate, global_context);

		kinc_file_reader_t reader;
		if (!kinc_file_reader_open(&reader, worker_data->fileName, KINC_FILE_TYPE_ASSET)) {
			kinc_log(KINC_LOG_LEVEL_ERROR, "Could not load file %s for worker thread", worker_data->fileName);
			exit(1);
		}

		size_t file_size = kinc_file_reader_size(&reader);
		char* code = new char[file_size + 1];
		kinc_file_reader_read(&reader, code, file_size);
		code[file_size] = 0;
		kinc_file_reader_close(&reader);

		Local<String> source = String::NewFromUtf8(isolate, code, NewStringType::kNormal).ToLocalChecked();

		TryCatch try_catch(isolate);
		Local<Script> compiled_script = Script::Compile(isolate->GetCurrentContext(), source).ToLocalChecked();

		Local<Value> result;
		if (!compiled_script->Run(context).ToLocal(&result)) {
			handle_exception(isolate, &try_catch);
		}

		while (!message_port->isTerminated) {
			double time = kinc_time();
			for (int i = 0; i < interval_functions.functions.size(); ++i) {
				if (interval_functions.functions[i].nextCallTime <= time) {
					TryCatch try_catch(isolate);
					Local<v8::Function> func = Local<v8::Function>::New(isolate, interval_functions.functions[i].function);
					Local<Value> result;

					if (!func->Call(context, context->Global(), 0, NULL).ToLocal(&result)) {
						handle_exception(isolate, &try_catch);
					}

					interval_functions.functions[i].nextCallTime = time + interval_functions.functions[i].interval;
				}
			}

			handle_message_queue(isolate, global_context, &message_port->ownerMessages);

			handle_worker_messages(isolate, global_context);
		}

		ContextData* context_data = (ContextData*)isolate->GetData(worker_data_slot);

		for (int i = 0; i < context_data->workers.size(); ++i) {
			WorkerMessagePort* workerPort = context_data->workers[i].workerMessagePort;
			workerPort->isTerminated = true;
			kinc_thread_wait_and_destroy(context_data->workers[i].workerThread);

			delete context_data->workers[i].workerThread;
			kinc_mutex_destroy(&context_data->workers[i].workerMessagePort->ownerMessages.messageMutex);
			kinc_mutex_destroy(&context_data->workers[i].workerMessagePort->workerMessages.messageMutex);
			kinc_mutex_destroy(&workerPort->ownerMessages.messageMutex);
			kinc_mutex_destroy(&workerPort->workerMessages.messageMutex);
			delete workerPort;
		}

		delete[] code;
		delete worker_data;
		delete context_data;
		// isolate->TerminateExecution();
	}

	void owner_onmessage_get(Local<String> property,const PropertyCallbackInfo<Value>& info) {
		Isolate* isolate = info.GetIsolate();
		HandleScope scope(isolate);

		Local<External> external = Local<External>::Cast(info.This()->GetInternalField(0));
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();

		info.GetReturnValue().Set(messagePort->workerMessages.messageFunc);
	}

	void owner_onmessage_set(Local<String> property, Local<Value> value, const PropertyCallbackInfo<Value>& info) {
		Isolate* isolate = info.GetIsolate();
		HandleScope scope(isolate);

		Local<External> external = Local<External>::Cast(info.This()->GetInternalField(0));
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();

		set_onmessage(&messagePort->workerMessages, isolate, value);
	}

	void owner_add_event_listener(const FunctionCallbackInfo<Value>& args) {
		Isolate* isolate = args.GetIsolate();
		HandleScope scope(isolate);

		if (args.Length() < 2) {
			return;
		}

		Local<String> name = Local<String>::Cast(args[0]);
		char event_name[256];
		int length = name->WriteUtf8(isolate, event_name, 255);
		event_name[length] = 0;
		if (strcmp(event_name, "message") != 0) {
			kinc_log(KINC_LOG_LEVEL_WARNING, "Trying to add listener for unknown event %s", event_name);
			return;
		}

		Local<External> external = Local<External>::Cast(args.This()->GetInternalField(0));
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();

		set_onmessage(&messagePort->workerMessages, isolate, args[1]);
	}

	void owner_post_message(const FunctionCallbackInfo<Value>& args) {
		Isolate* isolate = args.GetIsolate();
		HandleScope scope(isolate);

		if (args.Length() < 1) {
			return;
		}
		if (args.Length() > 1) {
			kinc_log(KINC_LOG_LEVEL_WARNING, "Krom workers only support 1 argument for postMessage");
		}

		Local<External> external = Local<External>::Cast(args.This()->GetInternalField(0));
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();

		post_message(&messagePort->ownerMessages, isolate, args[0]);
	}

	void owner_worker_terminate(const FunctionCallbackInfo<Value>& args) {
		Isolate* isolate = args.GetIsolate();
		HandleScope scope(isolate);

		Local<External> external = Local<External>::Cast(args.This()->GetInternalField(0));
		WorkerMessagePort* messagePort = (WorkerMessagePort*)external->Value();

		messagePort->isTerminated = true;

		ContextData* context_data = (ContextData*)isolate->GetData(worker_data_slot);
		for (std::vector<OwnedWorker>::iterator it = context_data->workers.begin(); it != context_data->workers.end(); ++it) {
			if (it->workerMessagePort == messagePort) {
				kinc_thread_wait_and_destroy(it->workerThread);
				context_data->workers.erase(it);
				break;
			}
		}

		kinc_mutex_destroy(&messagePort->ownerMessages.messageMutex);
		kinc_mutex_destroy(&messagePort->workerMessages.messageMutex);
		delete messagePort;

		args.This()->SetInternalField(0, External::New(isolate, nullptr));
	}

	void worker_constructor(const FunctionCallbackInfo<Value>& args) {
		Isolate* isolate = args.GetIsolate();
		HandleScope scope(isolate);
		if (!args.IsConstructCall()) {
			isolate->ThrowException(String::NewFromUtf8(isolate, "Worker constructor: 'new' is required").ToLocalChecked());
			return;
		}

		if (args.Length() < 1) {
			isolate->ThrowException(String::NewFromUtf8(isolate, "Worker constructor: At least 1 argument required, but only 0 passed").ToLocalChecked());
			return;
		}

		if (args.Length() > 1) {
			kinc_log(KINC_LOG_LEVEL_WARNING, "Krom only supports one argument for worker constructor, ignoring extra arguments");
		}

		WorkerMessagePort* messagePort = new WorkerMessagePort;
		kinc_mutex_init(&messagePort->ownerMessages.messageMutex);
		kinc_mutex_init(&messagePort->workerMessages.messageMutex);

		Local<Context> context = isolate->GetCurrentContext();

		Local<ObjectTemplate> templ = ObjectTemplate::New(isolate);
		templ->SetInternalFieldCount(1);
		Local<Object> worker = templ->NewInstance(context).ToLocalChecked();
		worker->SetInternalField(0, External::New(isolate, messagePort));

		Local<Value> prototype = context->Global()->Get(context, String::NewFromUtf8(isolate, "WorkerPrototype").ToLocalChecked()).ToLocalChecked();
		worker->SetPrototype(context, prototype);

		args.GetReturnValue().Set(worker);

		// Create thread and add it to list in context data
		OwnedWorker owned_worker;
		owned_worker.workerMessagePort = messagePort;
		owned_worker.workerThread = new kinc_thread_t;
		WorkerData* worker_data = new WorkerData;
		worker_data->messagePort = messagePort;
		Local<String> file_name = Local<String>::Cast(args[0]);
		int length = file_name->WriteUtf8(isolate, worker_data->fileName, 255);
		worker_data->fileName[length] = 0;

		// Check if file exists before we create thread
		kinc_file_reader fileCheck;
		if (!kinc_file_reader_open(&fileCheck, worker_data->fileName, KINC_FILE_TYPE_ASSET)) {
			const char* errorFmt = "Worker constructor: file %s does not exist";
			int length = snprintf(nullptr, 0, errorFmt, worker_data->fileName);
			char* errorMessage = (char*)malloc(length + 1);
			snprintf(errorMessage, length, errorFmt, worker_data->fileName);
			isolate->ThrowException(String::NewFromUtf8(isolate, errorMessage).ToLocalChecked());
			free(errorMessage);
			return;
		}
		kinc_file_reader_close(&fileCheck);

		kinc_thread_init(owned_worker.workerThread, worker_thread_func, worker_data);

		ContextData* context_data = (ContextData*)(isolate->GetData(worker_data_slot));
		context_data->workers.push_back(owned_worker);
	}
}

void bind_worker_class(Isolate* isolate, const v8::Global<v8::Context>& context) {
	Isolate::Scope isolate_scope(isolate);
	HandleScope handle_scope(isolate);

	Local<Context> current_context = Local<Context>::New(isolate, context);
	Context::Scope context_scope(current_context);
	Local<Object> global = current_context->Global();

	global->Set(current_context, String::NewFromUtf8(isolate, "Worker").ToLocalChecked(), Function::New(current_context, worker_constructor).ToLocalChecked());

	Local<ObjectTemplate> worker_prototype_templ = ObjectTemplate::New(isolate);

	worker_prototype_templ->SetAccessor(String::NewFromUtf8(isolate, "onmessage").ToLocalChecked(), (AccessorGetterCallback)owner_onmessage_get, (AccessorSetterCallback)owner_onmessage_set);
	worker_prototype_templ->Set(String::NewFromUtf8(isolate, "addEventListener").ToLocalChecked(), FunctionTemplate::New(isolate, owner_add_event_listener));
	worker_prototype_templ->Set(String::NewFromUtf8(isolate, "postMessage").ToLocalChecked(), FunctionTemplate::New(isolate, owner_post_message));
	worker_prototype_templ->Set(String::NewFromUtf8(isolate, "terminate").ToLocalChecked(), FunctionTemplate::New(isolate, owner_worker_terminate));

	global->Set(current_context, String::NewFromUtf8(isolate, "WorkerPrototype").ToLocalChecked(), worker_prototype_templ->NewInstance(current_context).ToLocalChecked());

	ContextData* context_data = new ContextData;
	isolate->SetData(worker_data_slot, context_data);
}

void handle_worker_messages(v8::Isolate* isolate, const v8::Global<v8::Context>& context) {
	Locker locker(isolate);
	Isolate::Scope isolate_scope(isolate);
	HandleScope handle_scope(isolate);

	ContextData* context_data = (ContextData*)(isolate->GetData(worker_data_slot));
	if (!context_data) { // FIXME: patch to prevent crash when `context_data` is null
		return;
	}
	if (context_data->workers.size() == 0) {
		return;
	}

	for (OwnedWorker& worker : context_data->workers) {
		handle_message_queue(isolate, context, &worker.workerMessagePort->workerMessages);
	}
}
