#include <Python.h>

static PyObject* create_list(PyObject* self, PyObject* args) {
    PyObject* list;
    PyObject* num1;
    PyObject* num2;

    list = PyList_New(2);  
    if (list == NULL) {
        return NULL;  
    }

    num1 = PyLong_FromLong(10);  
    num2 = PyLong_FromLong(15); 

    if (num1 == NULL || num2 == NULL) {
        Py_XDECREF(list);  
        return NULL;
    }

    PyList_SetItem(list, 0, num1);  
    PyList_SetItem(list, 1, num2); 

    return list;
}

static PyMethodDef example_methods[] = {
    {"create_list", create_list, METH_NOARGS, "Create a list of two numbers"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef example_module = {
    PyModuleDef_HEAD_INIT,
    "example", 
    "A simple example module", 
    -1,          
    example_methods  
};


PyMODINIT_FUNC PyInit_example(void) {
    return PyModule_Create(&example_module);
}