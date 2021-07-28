import os 

class SSApi:
    """Simple Switch CLI wrapper
    """
    def query(self, cmd):
        """execute an SSC command

        Args:
            cmd (string): the command to be executed

        Returns:
            string: the result of the the command
        """
        return os.popen(f'echo "{cmd}" | simple_switch_CLI').read()

    def push(func, *args, **kwargs):
        """A decorator for executing the defined commands

        Args:
            func (function): the result of this function is 
            executed in SSC
        """
        def wraper(self, *args, **kwargs):
            self.query(func(self, *args, **kwargs))
        return wraper

    def _table_add_str(self, tname, action, match, params):
        """Generate the table_add command 

        Args:
            tname (string): table name
            action (string): action to be performed
            match (list(int)): list of match values
            params (list(int)): list of parameters to be passed to the action

        Returns:
            string: table_add command
        """
        return ' '.join([
            f"table_add",
            f"{tname}",
            f"{action}",
            *[str(x) for x in match],
            f"=>",
            *[str(x) for x in params]
        ])

    @push
    def table_add(self, tname, action, match, params):
        """Generate table_add command and execute it

        Returns:
            None: the decorator consumes the return
        """
        return self._table_add_str(tname, action, match, params)

    @push
    def table_add_bulk(self, tname, amp):
        """Generate table_add commands and execute them in bulk.
        More efficient than table_add, when multiple entries
        must be added to the same table at once

        Args:
            tname (string): table name
            amp (list((a, b, c))): a - action, b - list of matches, c - list of params

        Returns:
            None: the decorator consumes the return
        """
        return '\n'.join([
            self._table_add_str(tname, amp[i][0], amp[i][1], amp[i][2]) 
                                                        for i in range(len(amp))
        ])

    @push
    def table_delete(self, tname, handle=None, keys=None):
        """Delete an entry from a table. handle xor keys must be defined.

        Args:
            tname (string): table name
            handle (int, optional): the handle of the table entry. Defaults to None.
            keys (list(int), optional): a list of keys that identify an entry. Defaults to None.

        Raises:
            Exception: happens when !(handle xor keys)

        Returns:
            None: the decorator consumes the return
        """
        if (keys is None) == (handle is None):
            raise Exception(f'SSApi(table_delete) : '
                            f'handle({handle}) xor key({keys}) must be specified')
        if keys is not None:
            handle = self.get_handle_from_key(tname, keys)
        return f'table_delete {tname} {handle}'

    @push
    def register_write(self, rname, idx, val):
        """Write a value to a register

        Args:
            rname (string): register name
            idx (int): index
            val (int): value to be written

        Returns:
            None: the decorator consumes the return
        """
        return f'register_write {rname} {idx} {val}'

    def register_read(self, rname, idx):
        """Read a value from a register

        Args:
            rname (string): register name
            idx (int): index

        Returns:
            int: the value of the register
        """
        out = self.query(f'register_read {rname} {idx}')
        return int(out.splitlines()[3].split()[-1])

    def get_handle_from_key(self, tname, keys):
        """Get table entry handle given a list of keys

        Args:
            tname (string): table name
            keys (list(int)): list of keys of a specific entry

        Returns:
            int: table entry handle
        """
        out = self.query(f'table_dump_entry_from_key {tname} '
                         f"{' '.join([str(x) for x in keys])} ")
        return int(out.splitlines()[3].split()[-1],16)

    def __enter__(self):
        return SSApi()

    def __exit__(self, *args, **kwargs):
        pass