import gc
import sys
def show_memory():
	print("*" * 60)
	objects_list = []
	for obj in gc.get_objects():
		size = sys.getsizeof(obj)
		objects_list.append((obj, size))
	sorted_values = sorted(objects_list, key = lambda x:x[1], reverse = True)

	for obj, size in sorted_values[:10]:
		print(f"OBJ: {id(obj)},"
			  f"Type: {type(obj)},"
			  f"Size: {size/1024/1024:.2f}MB,"
			  f"Repr: {str(obj)[:100]}")