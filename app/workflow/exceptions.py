class WorkflowError(Exception):
    pass

class WorkflowInputError(WorkflowError):
    pass

class WorkflowExecutionError(WorkflowError):
    pass

class WorkflowNoModelResponseError(WorkflowExecutionError):
    pass

