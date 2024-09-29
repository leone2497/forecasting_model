streamlit.errors.DuplicateWidgetID: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 88, in exec_func_with_error_handling
    result = func()
             ^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 590, in code_to_exec
    exec(code, module.__dict__)
File "/mount/src/forecasting_model/asset_model.py", line 136, in <module>
    st.download_button(label="Download Asset Combinations CSV",
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/metrics_util.py", line 410, in wrapped_func
    result = non_optional_func(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/elements/widgets/button.py", line 362, in download_button
    return self._download_button(
           ^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/elements/widgets/button.py", line 641, in _download_button
    button_state = register_widget(
                   ^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/state/widgets.py", line 167, in register_widget
    return register_widget_from_metadata(metadata, ctx, widget_func_name, element_type)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/state/widgets.py", line 209, in register_widget_from_metadata
    raise DuplicateWidgetID(
