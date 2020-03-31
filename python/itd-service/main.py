# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.dp import Action
import traceback

class ConfigureITD(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name, ' ', uinfo.actx_thandle, ' ', uinfo.username, ' ', uinfo.context)
        try:
            maapi = ncs.maapi.Maapi()
            maapi.attach2(0, 0, uinfo.actx_thandle)
            trans = ncs.maapi.Transaction(maapi, uinfo.actx_thandle)
            lb = ncs.maagic.get_node(trans, kp)
            service = lb._parent._parent._parent
            site = service._parent._parent
            self.log.info('Configuring ITD: '+service.deployment_name)
            run_root = ncs.maagic.get_root(trans)
            for service_device in service.device:
                for side in service.scaling.load_balance.cisco_intelligent_traffic_director.sides:
                    for nexus_device in site.intelligent_traffic_director.devices:
                        if nexus_device.side == side.side:
                            vars = ncs.template.Variables()
                            vars.add('SERVICE-NAME', service.deployment_name)
                            vars.add('DEVICE-NAME', nexus_device.device)
                            vars.add('SIDE', side.side)
                            vars.add('INGRESS-INTERFACE-NAME', side.ingress_interface)
                            vars.add('SERVICE-IP-ADDRESS', side.virtual_ip)
                            vars.add('SERVICE-IP-MASK', side.virtual_ip_mask)
                            if side.side == 'inside':
                                address = service_device.inside_ip_address
                            else:
                                address = service_device.outside_ip_address
                            vars.add('NODE-IP', address)
                            vars.add('SERVICE-BUCKET-COUNT', side.buckets);
                            template = ncs.template.Template(service)
                            template.apply('itd-service', vars)
                            self.log.info("ITD Add: {} {} {} {}".format(nexus_device.device, service_device.name, side.side, address))
                service.scaling.load_balance.status = 'Enabled'
                result =  "ITD Enabled"
                self.log.info("ITD Configured!")
        except Exception as e:
            self.log.error(e)
            self.log.error(traceback.format_exc())
            result = "Error: {}".format(e)
        finally:
            output.result = result

class Initialize(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name, ' ', uinfo.actx_thandle, ' ', uinfo.username, ' ', uinfo.context)
        self.log.info('Initialization Starting')
        try:
            maapi = ncs.maapi.Maapi()
            maapi.attach2(0, 0, uinfo.actx_thandle)
            trans = ncs.maapi.Transaction(maapi, uinfo.actx_thandle)
            lb = ncs.maagic.get_node(trans, kp)
            root = ncs.maagic.get_root(trans)
            service = lb._parent._parent._parent
            site = service._parent._parent
            result = "ITD Disabled"
            if service.scaling.load_balance.status in ('Unknown', 'Initialized'):
                self.log.info('Initializating {}'.format(service.deployment_name))
                kicker = root.kickers.data_kicker.create('itd-{}-{}-{}-{}'.format('ServiceSynchronized', service.tenant, \
                                                         service.deployment_name, 'configure-itd'))
                kick_monitor_node = ("/vnf-manager/site[name='{}']/vnf-deployment[tenant='{}'][deployment-name='{}']").format(
                                     site.name, service.tenant, service.deployment_name)
                trigger_expr = "status='Synchronized'"
                kick_node = ("/vnf-manager/site[name='{}']/vnf-deployment[tenant='{}'][deployment-name='{}']" +
                             "/scaling/load-balance/cisco-intelligent-traffic-director").format( \
                             site.name, service.tenant, service.deployment_name)
                kicker.monitor = kick_monitor_node
                kicker.trigger_expr = trigger_expr
                kicker.kick_node = kick_node
                kicker.action_name = 'configure-itd'
                kicker.priority = 3
                kicker.trigger_type = 'enter'
                service.scaling.load_balance.status = 'Initialized'
                result =  "ITD Initialized"
                self.log.info('Initialization for {} Complete'.format(service.deployment_name))
        except Exception as e:
            self.log.error(e)
            self.log.error(traceback.format_exc())
            result = "Error: {}".format(e)
        finally:
            output.result = result

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_action('configure-itd-action', ConfigureITD)
        self.register_action('initialize-itd-action', Initialize)

