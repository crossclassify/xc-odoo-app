/** @odoo-module */

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SetupForm extends Component {
  state = useState({
    setBefore: false,
    apikey: "",
    siteId: "",
    projectId: "",
    authToken: ""
  });

  setup() {
    console.log("setup");
    this.rpc = useService("rpc");
    onWillStart(async () => {
      this.data = await this.loadData();
    });
  }

  async loadData() {
    console.log("Trying to read settings");
    const resConfig = await this.rpc("/cc_smart_2fa/get_setup_data", {});
    console.log("resConfig", resConfig);
    if (resConfig.apikey && resConfig.siteId && resConfig.projectId) {
      console.log("existed");
      this.state.apikey = resConfig.apikey;
      this.state.siteId = resConfig.siteId;
      this.state.projectId = resConfig.projectId;
      this.state.authToken = resConfig.authToken
      this.state.setBefore = true;
    }
    console.log("not existed");
  }

  async saveCredentials() {
    console.log("Trying to save settings");
    await this.rpc("/cc_smart_2fa/set_setup_data", {
      apikey: this.state.apikey,
      siteId: this.state.siteId,
      projectId: this.state.projectId,
      authToken: this.state.authToken
    });
    console.log("saved successfuly");
    this.state.setBefore = true;
  }

  updateApikey(event) {
    this.state.apikey = event.target.value;
    console.log("Apikey Updated:", this.state.apikey);
  }

  updateProjectId(event) {
    this.state.projectId = event.target.value;
    console.log("ProjectId Updated:", this.state.projectId);
  }

  updateSiteId(event) {
    this.state.siteId = event.target.value;
    console.log("SiteId Updated:", this.state.siteId);
  }

  updateAuthToken(event) {
    this.state.authToken = event.target.value;
    console.log("SiteId Updated:", this.state.authToken);
  }
}

SetupForm.template = "cc_odoo_app.SetupForm";
