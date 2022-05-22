# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class Project(models.Model):
    _inherit = "project.project"

    #@api.multi
    def _compute_jobcost_count(self):
        jobcost = self.env['job.costing']
        job_cost_ids = self.mapped('job_cost_ids')
        for project in self:
            project.job_cost_count = jobcost.search_count([('id', 'in', job_cost_ids.ids)])
    
    
    job_cost_count = fields.Integer(
        compute='_compute_jobcost_count'
    )
    
    job_cost_ids = fields.One2many(
        'job.costing',
        'project_id',
    )

    project_number = fields.Char(string='Project Number')

    @api.constrains('project_number')
    def _check_project_number(self):
        record = self.env['project.project'].search([('id', '!=', self.id)])
        for project in record:
            if project.project_number:
                if project.project_number == self.project_number:
                    raise ValidationError(
                        'Project Number must be unique !!')

    #@api.multi
    def project_to_jobcost_action(self):
        job_cost = self.mapped('job_cost_ids')
        action = self.env.ref('job_costing_management.action_job_costing').read()[0]
        action['domain'] = [('id', 'in', job_cost.ids)]
        action['context'] = {'default_project_id':self.id,'default_analytic_id':self.analytic_account_id.id,'default_user_id':self.user_id.id}
        return action


class ProjectTask(models.Model):
    _inherit = 'project.task'

    #@api.multi
    def _compute_jobcost_count(self):
        jobcost = self.env['job.costing']
        job_cost_ids = self.mapped('job_cost_ids')
        for task in self:
            task.job_cost_count = jobcost.search_count([('id', 'in', job_cost_ids.ids)])

    job_cost_count = fields.Integer(
        compute='_compute_jobcost_count'
    )

    job_cost_ids = fields.One2many(
        'job.costing',
        'task_id',
    )

    job_order_number = fields.Char(string='Job Order Number')

    @api.constrains('job_order_number')
    def _check_job_order_number(self):
        record = self.env['project.task'].search([('id', '!=', self.id)])
        for task in record:
            if task.job_order_number:
                if task.job_order_number == self.job_order_number:
                    raise ValidationError(
                        'Job Order Number must be unique !!')

    #@api.multi
    def task_to_jobcost_action(self):
        job_cost = self.mapped('job_cost_ids')
        action = self.env.ref('job_costing_management.action_job_costing').read()[0]
        action['domain'] = [('id', 'in', job_cost.ids)]
        action['context'] = {'default_task_id':self.id,'default_project_id':self.project_id.id,'default_analytic_id':self.project_id.analytic_account_id.id,'default_user_id':self.user_id.id}
        return action

#odoo11

#class ProjectIssue(models.Model):
#    _inherit = 'project.issue'
#    
#    #@api.multi
#    def _compute_jobcost_count(self):
#        jobcost = self.env['job.costing']
#        job_cost_ids = self.mapped('job_cost_ids')
#        for task in self:
#            task.job_cost_count = jobcost.search_count([('id', 'in', job_cost_ids.ids)])
#    
#    
#    job_cost_count = fields.Integer(
#        compute='_compute_jobcost_count'
#    )
#    
#    job_cost_ids = fields.One2many(
#        'job.costing',
#        'issue_id',
#    )
#    
#    #@api.multi
#    def issue_to_jobcost_action(self):
#        job_cost = self.mapped('job_cost_ids')
#        action = self.env.ref('job_costing_management.action_job_costing').read()[0]
#        action['domain'] = [('id', 'in', job_cost.ids)]
#        action['context'] = {'default_issue_id':self.id,'default_task_id':self.task_id.id,'default_project_id':self.project_id.id,'default_analytic_id':self.project_id.analytic_account_id.id,'default_user_id':self.user_id.id}
#        return action
        
        
        
