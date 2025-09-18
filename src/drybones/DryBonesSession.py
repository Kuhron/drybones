class DryBonesSession:
    def __init__(self, drybones_dir_name: str, project_config_file_name: str):
        self.drybones_dir_name = drybones_dir_name
        self.project_config_file_name = project_config_file_name
    
    # TODO figure out how to cleanly add stuff to this like:
    # - known analyses by wordform
    # - corpus dir (although this is dependent on which fp we've passed to the command, should it be this way?)
    # - diacritics dict
    