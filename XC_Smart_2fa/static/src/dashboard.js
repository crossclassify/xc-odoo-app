/** @odoo-module **/

import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { HeroSection } from "./hero_section/hero_section";
import { SetupForm } from "./setup_form/setup_form";

class AwesomeDashboard extends Component {
  static template = "smart_2fa.AwesomeDashboard";
  static components = { Layout, HeroSection, SetupForm };

  setup() {
    this.action = useService("action");
    this.rpc = useService("rpc");
    this.display = {
      controlPanel: {},
    };
  }

  openCustomerView() {
    this.action.doAction("base.action_partner_form");
  }

  openLeads() {
    this.action.doAction({
      type: "ir.actions.act_window",
      name: "All leads",
      res_model: "crm.lead",
      views: [
        [false, "list"],
        [false, "form"],
      ],
    });
  }
}

registry.category("actions").add("smart_2fa.dashboard", AwesomeDashboard);
