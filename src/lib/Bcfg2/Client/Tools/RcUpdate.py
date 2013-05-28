"""This is rc-update support."""

import os
import Bcfg2.Client.Tools
import Bcfg2.Client.XML


class RcUpdate(Bcfg2.Client.Tools.SvcTool):
    """RcUpdate support for Bcfg2."""
    name = 'RcUpdate'
    __execs__ = ['/sbin/rc-update', '/bin/rc-status']
    __handles__ = [('Service', 'rc-update')]
    __req__ = {'Service': ['name', 'status']}

    def get_enabled_svcs(self):
        """
        Return a list of all enabled services.
        """
        return [line.split()[0]
                for line in self.cmd.run(['/bin/rc-status',
                                          '-s']).stdout.splitlines()
                if 'started' in line]

    def verify_bootstatus(self, entry, bootstatus):
        """Verify bootstatus for entry."""
        # get a list of all started services
        allsrv = self.get_enabled_svcs()
        # check if service is enabled
        return entry.get('name') in allsrv

    def VerifyService(self, entry, _):
        """
        Verify Service status for entry.
        Assumes we run in the "default" runlevel.

        """
        entry.set('target_status', entry.get('status'))  # for reporting
        bootstatus = self.get_bootstatus(entry)
        if bootstatus is None:
            return True

        # check if init script exists
        try:
            os.stat('/etc/init.d/%s' % entry.get('name'))
        except OSError:
            self.logger.debug('Init script for service %s does not exist' %
                              entry.get('name'))
            return False

        current_bootstatus = self.verify_bootstatus(entry, bootstatus)
        current_srvstatus = self.check_service(entry)

        # FIXME: this only takes into account the bootstatus attribute
        if current_bootstatus:
            entry.set('current_status', 'on')
        else:
            entry.set('current_status', 'off')

        return (current_bootstatus and (bootstatus == 'on')) and \
               (current_srvstatus and (entry.get('status') == 'on'))

    def InstallService(self, entry):
        """Install Service entry."""
        self.logger.info('Installing Service %s' % entry.get('name'))
        bootstatus = entry.get('bootstatus')
        if bootstatus is not None:
            if bootstatus == 'on':
                # make sure service is enabled on boot
                bootcmd = '/sbin/rc-update add %s default'
            elif bootstatus == 'off':
                # make sure service is disabled on boot
                bootcmd = '/sbin/rc-update del %s default'
            bootcmdrv = self.cmd.run(bootcmd % entry.get('name')).success
            if self.setup['servicemode'] == 'disabled':
                # 'disabled' means we don't attempt to modify running svcs
                return bootcmdrv
            buildmode = self.setup['servicemode'] == 'build'
            if (entry.get('status') == 'on' and not buildmode) and \
               entry.get('current_status') == 'off':
                svccmdrv = self.start_service(entry)
            elif (entry.get('status') == 'off' or buildmode) and \
                 entry.get('current_status') == 'on':
                svccmdrv = self.stop_service(entry)
            else:
                svccmdrv = True  # ignore status attribute
            return bootcmdrv and svccmdrv
        else:
            # when bootstatus is 'None', status == 'ignore'
            return True

    def FindExtra(self):
        """Locate extra rc-update services."""
        allsrv = self.get_enabled_svcs()
        self.logger.debug('Found active services:')
        self.logger.debug(allsrv)
        specified = [srv.get('name') for srv in self.getSupportedEntries()]
        return [Bcfg2.Client.XML.Element('Service', type='rc-update',
                                         name=name)
                for name in allsrv if name not in specified]
